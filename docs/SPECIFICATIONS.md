# Nominal engineering specifications — no physical prototype built

| Parameter | Budget V1 | Standard V1 |
|---|---:|---:|
| Base X × Y × thickness | 420 × 180 × 10 mm | 500 × 250 × 10 mm |
| Outer nominal machine envelope | 420 × 180 × ≤165 mm | 500 × 250 × 300 mm |
| Spindle axis height above base bottom | 95 mm | 130 mm |
| Feed / take-up station X centres | 90 / 328 mm | 105 / 380 mm |
| Spindle axis Y | 90 mm | 125 mm |
| Drum core diameter | Ø60 mm | Ø90 mm |
| Maximum nominal flange outer diameter | Ø112 mm | Ø150 mm |
| Axial drum winding width | 75 mm | 100 mm |
| Traverse mechanical design travel | 80 mm (nominal) | 120 mm (nominal) |
| Fiber geometry baseline | Ø0.90 mm buffered | Ø0.25 mm coated |
| Calculated upper winding estimate | ~389.9 m | ~11,104.9 m |
| Fiber goal | 200–300 m | Up to 10,000 m |
| Nominal lead screw | T8, 8 mm lead per turn assumed | T8, 8 mm lead per turn assumed |
| Controller | ESP32, untested on hardware | ESP32, untested on hardware |
| Motors/drivers | 2×NEMA17 and 2×TMC2209 assumed | 2×NEMA17 and 2×TMC2209 assumed |
| Winding control | passive dancer, manual brake | sensor feedback reference + encoder |
| Guarding | assessment pending | acrylic panels concept, mechanical interlock pending |

Nominal mechanical dimensions were derived to *stay within* the concept envelopes, not reverse-engineered to sub-mm precision from photographs. Printed spools are custom radial-web designs with through bolt holes; printed motor and bearing seats are nominal only. A spindle drive transmission of 1:1 is assumed and must be checked after purchasing pulleys.

**Caution:** for 10 km the 100 mm width and Ø150 flange are near the geometry ceiling. More clearance than assumed, wider coated fiber, flange structural requirements or damaged winding layers may invalidate the target. The owner can enlarge the machine (new standard variant) or narrow the fiber specification if validation shows insufficient margin; the present design must not silently change the owner's 500 × 250 × 300 mm target dimensions.
