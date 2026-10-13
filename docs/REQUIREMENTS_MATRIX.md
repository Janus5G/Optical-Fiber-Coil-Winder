# Gate 0 — concept and requirement traceability

Source of objectives: owner's two visual concept drawings and written hardware masterprompt, 2026-10-13. **Both original concept image files are embedded unchanged and SHA-256-inventoried in RC1.1.** The written dimensions and component list are used as traceable concept input; no hidden pixels or connector dimensions are being claimed.

| ID | Requirement | Source classification | Implemented evidence | Status |
|---|---|---|---|---|
| B01 | Budget compact base approx 350–450 × 120–180 mm | Owner concept | Parametric 420 × 180 mm base, max nominal z 151 mm | GEOMETRY TESTED / FIT HOLD |
| B02 | 200–300 m budget objective | Owner concept | Ø60/112 ×75 mm nominal 0.9 mm fiber scenario | GEOMETRIC FIT / PHYSICAL HOLD |
| B03 | Raspberry Pi Pico or ESP32 | Owner concept | ESP32 DevKitC selected as shared preliminary controller | PIN MAP REVIEW |
| B04 | Two NEMA17, two TMC2209, supply reel with brake, take-up spool, dancer, ceramic guides, traverse | Owner concept | CAD components and purchase references, host and embedded motion source | NOT PHYSICALLY VERIFIED |
| B05 | Budget 900–1,760 DKK | Owner concept price estimate | BOM allowance of 2,242 DKK | TARGET MISSED / RE-QUOTE |
| S01 | Standard envelope 500 × 250 × 300 mm | Owner concept | Modelled max nominal STEP envelope = 500 × 250 × 300 mm | GEOMETRY TESTED / FIT HOLD |
| S02 | Core options Ø60/70/80/90, outer ≤150 mm | Owner concept | Parametric core Ø90 / outer Ø150, all dimensions configurable in CAD source | OTHER CORES MUST BE EXPORTED/TESTED |
| S03 | Traverse 120 mm max; usable winding width 20–100 mm | Owner concept | Travel 120 mm, spool width 100 mm, margins 2 mm/side | GEOMETRIC DESIGN / FIT HOLD |
| S04 | 10 km up to use case | Owner aspiration | Ø90/150 ×100 mm and 250µm coated only: calculated ~11.1 km | GEOMETRY ONLY / FIBER PRODUCT HOLD |
| S05 | Encoder, load cell, feedback regulation, dancer | Owner concept | Simulated state logic + build-locked firmware reference; calibrated PID/P-controller not verified | HARDWARE TEST PENDING |
| S06 | Emergency stop, guard, protective stop | Owner requirement | External contactor/wiring concept; software build lock | SAFETY HOLD |
| C01 | Parametric parts, STEP/STL/DXF exports | Engineering deliverable | 26 part models + 2 assembly STEP + DXF/PNG/SVG | CREATED / FIT HOLD |
| C02 | Honest software tests and reproducibility | Engineering deliverable | Python unit tests and JSON PASS/FAIL/BLOCKED | SOFTWARE TESTED |
| C03 | Original images unchanged | Owner requirement | Original image files and SOURCE_MANIFEST.json SHA-256 | ATTACHED / SOURCE INTEGRITY TEST |
| C04 | Separate standalone repository; no GitHub action | Owner requirement | Independent package generated locally | MET |
| C05 | Research license keeps owner's commercial rights | Owner requirement | Candidate terms for owner approval; all-rights-reserved placeholder | LEGAL REVIEW HOLD |

## Engineering assumptions explicitly not derived from the images

- Shaft nominal diameter Ø8 mm, 608 bearings Ø8×22×7 mm, T8 leadscrew nominal lead 8 mm, NEMA17 front mounting pitch 31 mm, 1:1 belt drive and generic 5 mm motor shaft are **unverified purchase-fit assumptions**.
- Standard and Budget are mechanically different frames but share the same parametric part shapes; this does not imply a fully tolerance-checked assembly.
- Example fiber outside diameters .25, .9 and 2.0 mm do **not** identify a qualified fiber product.
- Calculated capacities assume orderly helical layering with 1.25× pitch and radial clearance and 2 mm axial margin on each side. Winding and optical performance may not achieve the geometric maximum.
- Model dimensions are nominal; no tolerance stack, resonance, strength, heat, motor torque, flanged spool stability or fatigue studies have been signed off.
