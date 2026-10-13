# v1.0.0-RC1.1 — Corrected engineering preview for owner review

**Distribution state:** Not yet a hardware manufacturing release or finalized public license. This is a candidate evidence package with dimensional design files and host software. No GitHub repository or commit is created by the generator.

**Design goals:** Budget 200–300 m, Standard up to 10 km only with suitable thin coated fiber and adequate tension/optical performance. Geometric estimates and physical test criteria are [separated](docs/VERIFICATION_REPORT.md).

**Corrected in RC1.1:** original owner-provided concept PNG images included byte-for-byte with SHA-256 source inventory. The mandatory CI host suite now installs CadQuery + ezdxf and fails on a missing dependency or skipped test.

**Open blockers:** supplier fit, 3D-printed strength, electrical ERC, safety circuit, calibration, firmware toolchain and board tests, optical OTDR/bend loss, full-length 10 km physical test, and license owner sign-off. No physical gate was changed to PASS.

**Source:** `tools/build_cad.py`, `common/fiber-calculations/fiber.py`, `common/controller/`, and `tests/`.

**Integrity:** `SHA256SUMS.txt` inventories files inside this release tree; external ZIP checksum is provided separately at distribution time.
