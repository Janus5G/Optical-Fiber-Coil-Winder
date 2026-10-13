# Changelog

## v1.0.0-RC1.1 — 2026-10-13

- Included the two original concept illustration PNGs unchanged, with recorded source filenames, file sizes and SHA-256.
- Corrected English/Danish READMEs, provenance notices, requirements and limitations to reflect the actual image attachments.
- Added a source-image integrity regression test; original SOURCE-16 blocker is resolved without affecting physical test HOLD.
- Pinned host-test dependencies; required CadQuery and ezdxf imports in GitHub CI so optional test skips cannot look like full validation.
- The release packager now refuses missing/skipped mandatory host checks.
- Retained unapproved research-license draft and all physical-safety/engineering holds; no hardware tests claimed.


## v1.0.0-RC1 — 2026-10-13

- Created independent Budget and Standard mechanical assemblies as parametric CadQuery source with STEP/STL/DXF export.
- Parameterized spool engineering at 200–300 m and 10 km design objectives, with fiber class caveats and automated scenario tables.
- Added ESP32 Arduino prototype source (motion build-locked), host control simulator, synthetic sensor/fault exercises and test harness.
- Added wiring overview diagrams, machine-specific estimate BOMs, English/Danish documentation, proposed owner-review license, and offline landing page.
- Introduced explicit HOLD on mechanical fit, safety review, supplier selection, physical fiber validation and original-illustration source attachment.
