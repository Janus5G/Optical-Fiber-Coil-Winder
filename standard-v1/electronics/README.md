# standard-v1 — electrical engineering HOLD

`concept_wiring.svg` is an architecture/wiring concept, **not** an electrically checked circuit schematic. No KiCad project or PCB fabrication approval is claimed.

- ESP32 DevKitC pins are based on the manufacturer user guide, but actual board variant, TMC2209 breakout wiring, logic levels, shared grounds, EMC and fusing must be verified against purchased modules.
- **External hardwired emergency stop and restart-prevention** must remove hazardous motor energy independently of the microcontroller; GPIO25 only monitors it.
- Add contact protection, strain relief, correct wire gauges, appropriate fuses and safe motor-drive power-off behavior following engineering review.
- Do not parallel-connect conflicting ESP32 power inputs. Prefer a qualified isolated 24 V power supply and a rated DC/DC 24-to-5 V converter for the MCU when not powered through USB.
- No motor energization is enabled in firmware as shipped: `ENABLE_REAL_MOTION=0`.
- ESP32 GPIO34/35/39 are input-only, lack internal pull-ups: use externally conditioned signals as required.

Official reference sources:
- ESP32 DevKitC V4: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html
- ADI TMC2209: https://www.analog.com/en/products/tmc2209.html

**Status: ENGINEERING CONCEPT ONLY / ELECTRICAL VERIFICATION REQUIRED.**
