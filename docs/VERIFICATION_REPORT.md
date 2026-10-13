# RC1.1 verification evidence — generated test inventory

Test date (UTC): 2026-10-13T06:39:38.333661+00:00

Host software/source-integrity checks: **47 PASS / 0 FAIL / 0 SKIP**. Hardware/other release qualification checks: **15 BLOCKED**.

This is not an approval to operate or manufacture. Nominal CAD dimensions are checked by geometric tests; manufactured hole tolerances, fit, electrical safety and optical signal integrity are **not verified**.

See [`PASS_FAIL_LOG.txt`](../results/PASS_FAIL_LOG.txt), [`test_report.json`](../results/test_report.json) and [`junit.xml`](../results/junit.xml). The benchmark fixture contains **synthetic host events only**. No physical fiber was wound and no sensor readings were taken.

## Critical holds

- Original owner-supplied concept illustrations are now attached unchanged, with SHA-256 source manifests; publication rights still require owner review.
- No hardware assembly, no independent emergency-stop qualification, no commissioning.
- No verified product-specific minimum bend radius or approved fiber tension settings.
- No measured shaft alignment, thermal behavior, print failure loads or load-cell calibration.
- No real test at 200–300 m or 10 km, and no optical insertion loss/OTDR evidence.
- No KiCad/ERC-ready design, no firmware build against a pinned ESP32 toolchain in this environment.
- Budget estimates are unquoted planning figures, not confirmed supply prices.

**Disposition: Software demonstrator/geometry engineering RC1 only; all prototype manufacturing and public "tested hardware" claims remain HOLD.**
