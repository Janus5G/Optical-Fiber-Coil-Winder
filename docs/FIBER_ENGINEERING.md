# Gate 1 — optical fiber engineering and coil capacity

This project calculates **available space only**. It does not identify a bend-safe or tension-safe fiber product and has not measured optical loss. Fiber jacket/coating **outside diameter**, not 125 µm glass cladding diameter, must be used as the winding diameter.

## Geometric model

Inputs: core outer diameter `D0`, maximum outer diameter `Dmax`, usable winding width `W - 2 margin`, outside fiber diameter `d`, traverse pitch factor `a≥1`, radial spacing factor `b≥1`.

For layer index `i=0,...,N-1`, centreline radius is `r_i = D0/2 + d/2 + i*b*d`. Pitch is `p = a*d` mm per turn. Turns per layer are `T = floor((W - 2*margin)/p)`. Available layers satisfy `D0/2 + d/2 + (N-1)*b*d + d/2 ≤ Dmax/2`.

Layer length `L_i = T * sqrt((2*pi*r_i)^2 + p^2) / 1000` metres, and total upper geometric estimate `L = sum_i L_i`.

This uses regular helical layering with straight traverse reversal assumptions. It is **not** a manufacturing process model and ignores turn crossing, winding defects, radial compression, flange edge roll-off, rotation acceleration, spindle deflection, end-layer waste and optical microbending.

The software reports available layers, turns/layer, target outer diameter, estimated time at constant surface speed and target total turns. It also checks user-supplied bend/tension limits. If limits are unknown or invalid it returns **HOLD**, never approval.

## Owner target scenario — pitch=radial=1.25×, margin 2 mm/side

| Machine | Fiber geometry | Theoretical max length | 300 m | 2 km | 10 km |
|---|---|---:|---|---|---|
| Budget Ø60→112, width 75 mm | 0.9 mm buffered | ~390 m | FIT (geometry) | NO | NO |
| Budget Ø60→112, width 75 mm | 2.0 mm jacketed | ~84 m | NO | NO | NO |
| Standard Ø90→150, width 100 mm | 0.25 mm coated | ~11,105 m | FIT | FIT | **FIT (geometry only)** |
| Standard Ø90→150, width 100 mm | 0.9 mm buffered | ~866 m | FIT | NO | NO |
| Standard Ø90→150, width 100 mm | 2.0 mm jacketed | ~171 m | NO | NO | NO |

All FIT entries are spatial model results only. They do NOT establish that winding and unwinding are possible without optical damage.

**Factory product specification check required:** fiber manufacturer/reel part number, actual coating diameter tolerance, permitted installation/static bend radius, rated spool/installation tension, temperature/humidity constraints, attenuation measurement bands and proof/handling specification. For example, a Corning SMF-28 Ultra product information sheet lists nominal coating diameters (242 or 200 µm depending on product option), demonstrating why 250 µm is a convenient **example**, not a universal truth. A patch cable rated at 20 mm installation bend radius does not confer that same value on bare coated fiber or another cable.

References (manufacturer/standards):
- [Corning SMF-28 Ultra product information sheet](https://www.corning.com/content/dam/corning/media/worldwide/coc/documents/Fiber/product-information-sheets/PI-1424-AEN.pdf) — coating diameter options, *not an approval for this winder*.
- [ITU-T G.657, 08/2024](https://www.itu.int/rec/T-REC-G.657-202408-I/en) — bending-loss-insensitive fiber classes, *not a winder product certification*.
- [ESP32 DevKitC manufacturer guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) for pin limitations.

## Speed and motion

For nominal fiber surface speed `v` mm/min, spindle RPM is `v/(2*pi*r)` and STEP frequency is `(RPM/60)*(motor_steps_per_rev*microstep_ratio)*(transmission_ratio)`. Traverse motion per spindle revolution is the chosen `p` mm; traversing a leadscrew with 8 mm assumed lead and 3200 microsteps/rev requires `3200*(p/8)` traverse steps per take-up revolution *if* motor-to-spindle drive ratios are 1:1. Other pulleys or actual lead screws demand corrected ratios.

The default 2 m/min produces a simple estimate of 150 minutes for 300 m and 5,000 minutes (~83.3 hours) for 10 km at constant surface speed, **excluding setup, acceleration, layer-reversal delays, breaks, cleaning and service**. Such duration means sustained thermal, coating friction and feed spool inertia become important in physical qualification.

## Optical test acceptance framework

Measure optical insertion loss/OTDR at appropriate product-rated wavelengths and compare pre/post winding under identical measurement setup; note instrument calibration, measurement uncertainty, splice/connectors and fiber lot. Acceptance thresholds must be assigned to a named fiber product and research protocol before testing. Record actual smallest transient bend radius including dancer/ceramic guide route, not just drum core radius.
