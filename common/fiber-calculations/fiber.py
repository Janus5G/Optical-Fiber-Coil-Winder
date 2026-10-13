"""Geometric fiber spool model, NOT an optical/tensile product qualification.
Standard library only; all linear dimensions millimetres except lengths in metres.
Copyright (c) 2026 Janus Rokkjær. License subject to LICENSE_REVIEW.md.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import argparse
import json
import math


@dataclass(frozen=True)
class Spool:
    core_diameter_mm: float
    outer_diameter_limit_mm: float
    winding_width_mm: float
    fiber_outer_diameter_mm: float
    pitch_factor: float = 1.10  # engineering assumption, configurable
    radial_factor: float = 1.10  # engineering assumption, configurable
    side_margin_mm: float = 1.0  # per-side margin
    # Must be specified from the EXACT fiber product's datasheet before qualification:
    manufacturer_min_bend_radius_mm: float | None = None
    manufacturer_max_tension_n: float | None = None
    design_winding_tension_n: float | None = None


def calculate(s: Spool, target_m: float | None = None, surface_speed_m_min: float = 2.0) -> dict:
    nums = [s.core_diameter_mm, s.outer_diameter_limit_mm, s.winding_width_mm,
            s.fiber_outer_diameter_mm, s.pitch_factor, s.radial_factor,
            s.side_margin_mm, surface_speed_m_min]
    if not all(math.isfinite(x) for x in nums):
        raise ValueError('nonfinite geometric/speed input')
    if s.core_diameter_mm <= 0 or s.fiber_outer_diameter_mm <= 0 or s.winding_width_mm <= 0:
        raise ValueError('dimensions must be positive')
    if s.outer_diameter_limit_mm <= s.core_diameter_mm:
        raise ValueError('outer diameter must exceed core')
    if s.pitch_factor < 1 or s.radial_factor < 1 or s.side_margin_mm < 0:
        raise ValueError('pitch/radial factor must be >= 1; margin >= 0')
    if surface_speed_m_min <= 0:
        raise ValueError('surface speed must be positive')
    for label, x in [('target', target_m), ('bend radius', s.manufacturer_min_bend_radius_mm),
                     ('rated tension', s.manufacturer_max_tension_n),
                     ('working tension', s.design_winding_tension_n)]:
        if x is not None and (not math.isfinite(x) or x <= 0):
            raise ValueError(f'{label} must be finite and positive')
    effective_width = s.winding_width_mm - 2 * s.side_margin_mm
    if effective_width <= 0:
        raise ValueError('side margins exceed winding width')
    pitch = s.fiber_outer_diameter_mm * s.pitch_factor
    radial_pitch = s.fiber_outer_diameter_mm * s.radial_factor
    turns_per_layer = math.floor(effective_width / pitch)
    # First coated fiber centreline sits one radius above the core; last outside surface <= OD limit.
    layers = math.floor(((s.outer_diameter_limit_mm - s.core_diameter_mm) / 2 -
                         s.fiber_outer_diameter_mm / 2) / radial_pitch) + 1
    layers = max(0, layers)
    if turns_per_layer == 0 or layers == 0:
        raise ValueError('geometry cannot accommodate a single winding')
    layer_lengths_m = []
    for layer in range(layers):
        center_radius = s.core_diameter_mm / 2 + s.fiber_outer_diameter_mm / 2 + layer * radial_pitch
        helical_turn_mm = math.hypot(2 * math.pi * center_radius, pitch)
        layer_lengths_m.append(helical_turn_mm * turns_per_layer / 1000)
    capacity_m = sum(layer_lengths_m)
    if target_m is None:
        target_m = capacity_m
    accumulated = 0.0
    turns_needed = 0
    layers_needed = 0
    outer_used = s.core_diameter_mm
    for i, length in enumerate(layer_lengths_m):
        if accumulated >= target_m - 1e-10:
            break
        needed = min(turns_per_layer, math.ceil((target_m - accumulated) /
                        (length / turns_per_layer)))
        accumulated += needed * length / turns_per_layer
        turns_needed += needed
        layers_needed = i + 1
        outer_used = s.core_diameter_mm + (2 * i * radial_pitch + s.fiber_outer_diameter_mm)
    # Existence of specifications does NOT verify their applicability to an assembly.
    bend_known = s.manufacturer_min_bend_radius_mm is not None
    tension_known = s.manufacturer_max_tension_n is not None and s.design_winding_tension_n is not None
    bend_ok = (s.core_diameter_mm / 2 >= s.manufacturer_min_bend_radius_mm) if bend_known else None
    tension_ok = (s.design_winding_tension_n <= s.manufacturer_max_tension_n) if tension_known else None
    geometrically_fits = target_m <= capacity_m + 1e-9
    qualification = ('DOCUMENTED_LIMITS_CONDITIONAL_ONLY' if bend_ok and tension_ok and geometrically_fits
                     else 'HOLD')
    return {
        'inputs': asdict(s), 'target_length_m': target_m,
        'surface_speed_m_min': surface_speed_m_min,
        'traverse_pitch_mm_per_turn': pitch, 'radial_step_mm_per_layer': radial_pitch,
        'usable_width_mm': effective_width, 'turns_per_layer': turns_per_layer,
        'layers_available': layers, 'capacity_m_geometric_upper_bound': round(capacity_m, 6),
        'geometrically_fits': geometrically_fits,
        'target_turns': turns_needed if geometrically_fits else None,
        'target_layers': layers_needed if geometrically_fits else None,
        'target_outer_diameter_mm': round(outer_used, 4) if geometrically_fits else None,
        'estimated_duration_min_at_constant_surface_speed': round(target_m / surface_speed_m_min, 3),
        'bend_limit_known': bend_known, 'bend_check_pass': bend_ok,
        'tension_limit_known': tension_known, 'tension_check_pass': tension_ok,
        'qualification': qualification,
        'warning': ('MODEL IS AN IDEALIZED SPATIAL PACKING ESTIMATE. NOT VERIFIED FOR '
                    'OPTICAL ATTENUATION, MICRO-BENDS, SPOOL FLANGE STRENGTH, '
                    'TENSION, REEL COMPATIBILITY, OR ACTUAL WIND QUALITY.')
    }


def main():
    p = argparse.ArgumentParser(description='Offline geometric coil sizing (NOT verified suitability)')
    p.add_argument('--core-mm', type=float, required=True)
    p.add_argument('--outer-mm', type=float, required=True)
    p.add_argument('--width-mm', type=float, required=True)
    p.add_argument('--fiber-mm', type=float, required=True)
    p.add_argument('--target-m', type=float, default=None)
    p.add_argument('--pitch-factor', type=float, default=1.10)
    p.add_argument('--radial-factor', type=float, default=1.10)
    p.add_argument('--side-margin-mm', type=float, default=1.0)
    p.add_argument('--min-bend-radius-mm', type=float, default=None)
    p.add_argument('--max-tension-n', type=float, default=None)
    p.add_argument('--working-tension-n', type=float, default=None)
    p.add_argument('--speed-m-min', type=float, default=2.0)
    a = p.parse_args()
    s = Spool(a.core_mm, a.outer_mm, a.width_mm, a.fiber_mm,
              a.pitch_factor, a.radial_factor, a.side_margin_mm,
              a.min_bend_radius_mm, a.max_tension_n, a.working_tension_n)
    print(json.dumps(calculate(s, a.target_m, a.speed_m_min), indent=2))


if __name__ == '__main__':
    main()
