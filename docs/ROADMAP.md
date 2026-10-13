# Development roadmap / release gates

- **RC1 (current):** nominal CAD + host fiber feasibility analysis, budget/standard BOM estimates, firmware prototypes, wiring overview and host tests. Hardware and owner-license approval HOLD.
- **Gate A — source artwork/provenance:** attach exact originals with SHA-256 and authorization; audit concept-dimension interpretation.
- **Gate B — procurement:** assign supplier, exact manufacturer part numbers, geometry/thermal specs, current prices and toolchain dependencies. Resolve Budget budget target without weakening safety.
- **Gate C — mechanical:** print samples, mate genuine bearing/motor/fasteners, verify travel/clearance and reel strength, update STEP/STL and test evidence.
- **Gate D — electrics/safety:** create reviewed KiCad electrical diagrams and wiring harness, verify TMC2209 modules and independent latching E-stop/guard interlock; complete independent safety assessment.
- **Gate E — firmware:** compile against pinned ESP32 platform, flash bench unit, test motion/timing/limits/encoder/load cell, dynamic feedback and failure behavior, retain hardware lock until accepted.
- **Gate F — optics:** pass short dummy-run tests and actual approved fibers, optical before/after tests, Budget 200/300 m and Standard phased lengths to 10 km.
- **Gate G — legal/public release:** owner approves exact research license and publication rights, update NOTICE and CITATION as needed; only then create a repository or tag by explicit owner authorization.

No existing external project or PRISME/Q8 system needs to be touched for any gate.
