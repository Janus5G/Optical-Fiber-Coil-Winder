# Future hardware test plan and record template — NO EXECUTED HARDWARE TESTS

Every physical test starts **BLOCKED** until an appropriate assembled prototype, calibrated instruments and safety sign-off exist. A software PASS may not be transferred to these tests.

| ID | Physical procedure | Suggested evidence | Pre-test requirement | Current result |
|---|---|---|---|---|
| HT01 | Compare purchased hardware with printed motor/bearing/bore fit | Manufacturer drawings, caliper/micrometer results | Verified parts and material coupons | BLOCKED |
| HT02 | Inspect E-stop electrical independence, reset and unexpected restart | Circuit review, continuity, safe power fault injections | Qualified electrical/safety reviewer | BLOCKED |
| HT03 | Verify guard strength and interlock, entanglement clearances | Photo log, probe/clearance measures | Guard and independent cutoff built | BLOCKED |
| HT04 | No-fiber slow empty-spindle rotation, dynamic balance/runout | Dial gauge, RPM, thermal log | HT01–HT03 passed | BLOCKED |
| HT05 | Traverse homing, repeatability, mechanical travel and stop | Digital indicator, end-switch logs | Independent safety gate passed | BLOCKED |
| HT06 | Dancer and feed brake static/dynamic behavior | Torque/force gauge readings | Completed calibration | BLOCKED |
| HT07 | Force limit and broken-fiber simulation with dummy media | Calibrated load cell, software and hardware safety logs | Validated threshold and fault tests | BLOCKED |
| HT08 | Bend path gauge check under real reel motion | Radius gauge, macro/microbend audit | Named fiber specifications | BLOCKED |
| HT09 | 1–2 m fiber wind and unwind | Fiber lot, microscopy, optical baseline | HT01–HT08 passed | BLOCKED |
| HT10 | 200–300 m Budget endurance/optical test | Actual length and loss trace | Qualified buffered fiber | BLOCKED |
| HT11 | Staged Standard 2 km then 10 km endurance | Temperature, runout, tension, tracking, cycle time, OTDR | Coated fiber product spec + prior phases | BLOCKED |
| HT12 | Optical loss/OTDR before/after winding and unwinding | Calibration, power meter/OTDR trace, wavelength | Fiber-specific criteria | BLOCKED |
| HT13 | Supply interruption, reset, jam and stuck input behavior | Hazard testing in protected fixture | Qualified reviewer | BLOCKED |
| HT14 | Sustained motor/driver thermal and power test | Thermocouple, load current, thermal images | Electrical safety sign-off | BLOCKED |

## Measured result sheet template (copy one per physical test)

```text
Test ID:
Machine, serial no., firmware build hash:
Date/time / engineer / independent witness:
Fiber manufacturer, product code, lot, coating OD:
Spool core / OD / width (as measured):
Motor, step drivers, encoder, load cell component IDs:
Supply voltage/current, temperature, humidity:
Instruments and calibration certificate references:
Method / sample size / measurement uncertainty:
Predefined acceptance threshold & reference to approved fiber rating:
Measurements (raw data filenames and SHA-256):
Observed equipment deviation or safety event:
Result: PASS / FAIL / BLOCKED (default BLOCKED)
Reviewer signature, review date:
Corrective actions and rerun link:
```

**Never pre-fill PASS.** Keep failed evidence and document patches/new tests with date and operator. No unsupported inferred stress or bend strength values are acceptable.
