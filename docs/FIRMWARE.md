# Embedded prototype control and test boundaries

## Source and target

- Shared ESP32 Arduino source: `common/controller/embedded/winder.hpp`.
- Budget ESP32 entrypoint: [Budget main.cpp](../budget-v1/firmware/src/main.cpp).
- Standard ESP32 entrypoint: [Standard main.cpp](../standard-v1/firmware/src/main.cpp).
- Pin map: [Budget CSV](../budget-v1/electronics/gpio_assignments.csv), [Standard CSV](../standard-v1/electronics/gpio_assignments.csv).

Compile project sketches using PlatformIO and the real ESP32 toolchain **only when available**; these binaries have not been compiled/flashed in this release environment. There is no released firmware binary. `ENABLE_REAL_MOTION` defaults to zero and is checked by host tests.

## Implemented source behavior (not board verified)

- Startup reads settings from Preferences/NVS if byte-size and numeric validation succeed. Motor driver enable is held high (off for assumed TMC2209 breakout polarity) and all motor commands are build-locked.
- `STATUS`, `TARGET meters`, `SPEED meters/min`, `STOP`, `PAUSE`, `HOME`, `START`, `RESET` serial operations. Standard prototype has `TARE`, `CAL_LOAD scale min_N setpoint_N max_N`, and `CAL_ENCODER pulses_per_rev` for engineering calibration.
- Simple homing reference attempts traverse motion toward normally closed home switch with timeout; normally-closed limit loops are read LOW when healthy and HIGH on triggered contact or disconnected wire; this is separate from the normally-closed stop/guard safety circuits.
- Take-up microstep generator and pitch-ratio accumulator for traverse, with reversal after the nominal usable number of winding turns. Estimated accumulated length uses radius by completed turns/layers, not measured actual fiber distance.
- Standard load cell read samples near 10 Hz and applies an *unvalidated* bounded proportional speed correction; excessive or low tension, unavailable sensor data, end switches, guard monitor and encoder discrepancy stop the software control path.
- A separately hardwired power removal circuit is required regardless of MCU behavior.

## Critical engineering gaps before unlocking motors

- Full 2-phase quadrature encoder handling, PWM/stable pulse timing under interrupt load, accurate mechanical pulley reduction and microstep setting consistency, 24 V TMC2209 breaker board matching, motor heating.
- Calibrated physical tension with stored signed tare across restarts and sensor drift, unambiguous sensor disconnect detection, tension-loop stability with actual brake/dancer inertia.
- A verified timebase including rollover and watchdog, monitored safe startup, actual electrical safety circuit, power loss restart prevention, thermal protection, real-time scheduler, mechanical protection and documented test coverage on target MCU.
- Robot/machine safety review: firmware is not a safety controller, regardless of error states in tests.

These gaps are release **HOLD**, not implementation successes. The host model (`common/controller/control.py`) separately verifies state-model intent and does not compile the embedded source.
