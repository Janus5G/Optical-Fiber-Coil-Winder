# Calibration and acceptance checklist — future physical work

**None of the steps here have been executed physically.** Record calibration certificates and source instruments in test evidence before changing HOLD to PASS.

## Geometric metrology

- Measure spindle metal shaft OD, bore axis offset and endplay with micrometre/dial indicator; compare manufacturer bearings with print coupons.
- Measure effective drum outside diameter and usable width including retained flange contact zone at three angular stations. Do not replace nominal code values with measured ones without recording changes.
- Characterize actual 8 mm nominal lead by commanding several complete traverse reversals and comparing against digital indicator travel. Test direction reversal backlash and anti-backlash nut play.
- Verify encoder pulses per **spool shaft** revolution with controlled manual spindle rotation; record phase/index behavior and pulley ratio, not only motor rotation.

## Tension and dancer

- Calibrate a load cell using traceable known low forces in the actual linkage geometry. A load cell full-scale mass label is not itself tension in Newtons at the fiber contact point.
- Establish zero offset at no applied fiber tension, measure scale, hysteresis, 10× repeatability, electrical noise and sign across the expected low-force range.
- Determine allowed steady, transient and break-detection thresholds **from the named fiber product** and experimentally qualified guide arrangement. Do not use simulator example 0.5 N as a product rating.
- Characterize dancer displacement, natural frequency, stop contact, brake startup torque and transient supply inertia; measure sensitivity of the prototype proportional speed correction and tune in a safe environment.

## Optical baseline

- Inspect connectors/end-face handling; measure optical loss and/or OTDR trace at the fiber manufacturer's specified wavelengths, meter range and test setup.
- Store instrument calibration, test uncertainty, environmental temperature/humidity, reel lot, reference jumpers, connector condition and operator.
- Test before winding, after winding and after unwinding. Separate connector variability and source drift from spool-induced loss.

## Firmware caution

The included sketch has **build-time motor activation disabled**. The serial `TARE` produces an offset valid for the current power session; `CAL_LOAD` and `CAL_ENCODER` save reference settings, but neither verifies physical calibration. A production firmware design must address persistent tare validity, sensor zero drift, full 2-channel encoder quadrature, P-controller dynamic stability, anti-windup (if PID adopted), clock wrap, motor step timing, actual transmission ratios and hazard analysis.

Calibration is supervised hardware engineering, not a ready-to-follow user quickstart for a powered machine.
