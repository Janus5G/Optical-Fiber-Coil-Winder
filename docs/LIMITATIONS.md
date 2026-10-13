# Known limitations and assumptions

1. **Source illustrations:** the two supplied PNGs are now bundled unchanged and verified against an image source manifest. They remain unverified concept representations, not evidence of a built device; publication rights require owner review.
2. **Dimensional certainty:** actual manufacturer bolt/hub/nut/roller dimensions, load paths and tolerances not verified. CAD outputs are nominal, **fit HOLD**.
3. **Strength:** printable drum's hoop strength, fatigue, heat, and fiber pressure limits have not been calculated against a proven material. 10 km use also needs mass/inertia/imbalance review.
4. **Winding model:** deterministic ideal helical-layer capacity is not a production fiber compatibility model. Fiber/coating slip, twist, crush, bends and changes in pitch invalidate estimates.
5. **Optical performance:** no photonic instruments, OTDR, loss measurements or temperature/endurance data acquired.
6. **Cost:** item prices are unquoted allowances dated 2026-10-13, excluding VAT, shipping, fiber, labour, reprints and equipment. Initial Budget concept cap of DKK 1,760 is exceeded by the estimate; source commercial prices must be verified.
7. **Electronics:** only labelled wiring architecture diagrams are supplied, no ERC-reviewed KiCad schematic, PCB, wiring harness detail or third-party certifications.
8. **Safety:** no externally engineered E-stop/restart circuit, verified guard materials or physical cutoff test; motors are intentionally build-locked in firmware.
9. **Firmware:** no PlatformIO build (not available on the original release host), no board flash, no verified motion/sensor timings; Standard proportional feedback is a conceptual algorithm with uncalibrated sensor.
10. **10 km endurance:** at a nominal 2 m/min surface feed 10 km takes ~83 hours continuous; motor longevity, brake heat, dancer behavior and unattended safety are unproven.
11. **Research license:** proposed research/noncommercial agreement not adopted by the owner; LICENSE retains all rights. Redistribution restrictions and potential patents require legal review.
12. **GitHub Actions:** workflow now installs required CAD libraries and fails if mandatory imports are missing. Hosted CI has not yet been run in a GitHub repository.
