# Safety and risk assessment — NO MACHINE APPROVAL

**Status: engineering conceptual risk assessment only. The motors are firmware build-locked OFF.** Neither a printed structure nor an ESP32 software input constitutes a certified guard, interlock or emergency stop. Machine use can cause hair entanglement, pinch/crush injuries, pulled fiber cuts/splinters, broken glass, electrical faults and fiber eye hazards if lit optical links are connected.

| Hazard / condition | Preliminary mitigation | Verification required |
|---|---|---|
| Exposed rotating reel, drive belt and pinch points | Mechanical barriers; no accessible moving gap during rotation | Guard strength/accessibility, hand/finger probe tests, fastener loads, safe access |
| Exposed optical fiber or fragments | Eye protection, safe disposal, guards, never examine live endface | Local lab procedure and optical source safety |
| Sudden tension rise / coating damage | Independent mechanical slip torque limit, gentle feed dancer and software measured stop in Standard | Actual force measurement and failure response |
| Unexpected restart after power return | Mechanical latching E-stop, contactor/reset that requires intentional restart | Hardwired test with lost and restored power, MCU crash, welded contacts failure analysis |
| MCU hung, GPIO stuck, motor driver fault | Independent hazardous motor supply energy cutoff | Fail-safe circuit design and physical destructive/fault-injection tests |
| Motor overheating / PSU fault | Fused supply, rated current setting, ventilated guard, safe wiring | Load/temperature tests and electrical review |
| Spool flange burst or shaft/bearing failure | Appropriate material, positive retention, supported spindle, guarding | Rotating-load/overspeed tests, balancing, material strength/creep tests |
| Traverse jams or runaway | Physical stops and normally closed home/far switches | Mechanical end-of-travel tests independent of code |
| Standard guard opened mid-cycle | Guard-rated interlock in independent motor safety circuit | Certified switch choice, physical gap/test plan |
| Supply reel inertia and torque | Adjustable low-force brake, dancer travel stops | Transient speed testing; monitored maximum tension |

## Mandatory hardware safety chain (not yet designed to production level)

1. Use an appropriately rated isolated DC supply; *do not* expose users to uncontained mains power or improvise mains terminal connections.
2. Install an external, latching, manually reset motor-energy isolation circuit, controlled by a chosen properly rated stop and any required guard interlocks. Its output must remove motor energy on E-stop, guard opening or fail-safe condition, independent of the ESP32.
3. Use a protected contactor/relay topology that prevents unintended restarting when the stop circuit is reset or mains returns. Set restart behavior independently of firmware.
4. The GPIO25 input is a **monitor only**, and the driver EN signal is an additional **functional stop only**. Neither is designated as an emergency-stop safety function.
5. Obtain review of safeguarding requirements for the intended geography/use and perform wiring inspection, fault analysis, electrical tests and operator validation before changing firmware `ENABLE_REAL_MOTION 0`.
6. Ensure no optical light source/laser is energized into a loose connector during assembly.

**Critical finding:** the budget concept's original "optional E-stop" is not carried forward as optional for any powered prototype; documented independent motor energy isolation is a mandatory safety gate. Standard guard material/design and interlock must still be chosen and validated. The current acrylic plate models are placeholders and have **not** passed impact/pinch protection validation.

Reference electronics architecture: [Budget wiring overview](../budget-v1/electronics/concept_wiring.svg) and [Standard wiring overview](../standard-v1/electronics/concept_wiring.svg). These are wiring concepts, **not reviewed electrical schematics**.
