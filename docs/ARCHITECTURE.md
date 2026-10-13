# System architecture — two independent mechanical builds

The supply spindle is passive and resisted by an adjustable mechanical brake. An inertial dancer roller between feed and take-up smooths transient speed differences. A ceramic fiber guide rides on a longitudinal traverse parallel to the take-up spool axis, driven by a T8 lead screw and a second NEMA17 stepper. Take-up rotation and traverse are kinematically related by the selected fiber pitch and shaft/motor transmission ratio.

- **Budget V1:** manually set brake, passive dancer, open-loop stepper commands and geometric **length estimate**. There is no verified tension sensor. Feed slip, step loss and coating damage cannot be ruled out by firmware.
- **Standard V1:** adds HX711/load-cell feedback, take-up encoder consistency reference, transparent physical guard proposal and a simple prototype speed-adjustment controller. Safety architecture is independent of processor control. Exact encoder quadrature edges, load-cell range, calibration, guard opening access and brake/dancer response need physical qualification.

![Budget engineering plan](../budget-v1/drawings/nominal_top_view.png)

![Standard engineering plan](../standard-v1/drawings/nominal_top_view.png)

## Coordinate convention

Machine base has origin at front-left-bottom corner (all values mm). X increases left to right across the two spindle stations. Y increases from front to back and is the axis of both spindle shafts and the traverse movement. Z increases vertically. All dimensions in `tools/build_cad.py` derive from version-specific values in `CFG`. Real motor faces, shaft center distances and belt clearance require procurement fit checks.

## Mechanical deliverables and intended process

- `cad/*.step` — nominal exchange solids, **not manufacturing-approved**.
- `cad/*.stl` — tessellations for inspection/test prints, not strength-qualified finished components. Metal shafts and commercial motors, bearings, roller and pulleys must be purchased, not replaced with printed load-bearing equivalents.
- `cad/assembly_nominal.step` — visual compound of nominal supports and reference rods; does **not** include full fastening, electrical wiring, coupling and belt geometry.
- `drawings/base_drill_pattern.dxf` — hole pattern with common source geometry from the base STL/STEP.
- `drawings/nominal_top_view.png` — nominal engineering top view with base dimensions.

## Component verification

1. Verify manufacturer drawings for actual purchased NEMA17 frame and shaft, TMC2209 breakout board, ceramic guides, rollers, HX711, load cell, switch and encoder.
2. Re-run CAD after replacing nominal parameters with purchased dimensions, and check motor/shaft/belt alignment.
3. Print a fit coupon (motor holes, bearing Ø22.2 nominal seat, flange bolt holes) **before** any complete drum.
4. Inspect STL bounding boxes and mechanically measure holes/surfaces; acknowledge print process tolerances and material relaxation.
5. Address unsupported printed flange strength and thermal/creep limits before rotational trials.
6. Verify traverse rods/lead screw end-to-end bearing clearance with the 120 mm design travel; verify limit sensor physical actuators.

## Firmware architecture

ESP32 Arduino prototype in `common/controller/embedded/winder.hpp`, included by two standalone variant PlatformIO entrypoints. Serial commands are available for status, settings and diagnostic stop, but **motor GPIO is held disabled by `ENABLE_REAL_MOTION 0`** as supplied. A standard-mode calibrated load cell and encoder settings must exist before the software control path permits start; this does not substitute for the hardwired safe energy isolation.

The host simulator in `common/controller/control.py` is a separate reproducible mathematical state machine. Its PASS results never prove embedded real-time performance.
