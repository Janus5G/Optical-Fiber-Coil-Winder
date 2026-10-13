"""Generate clearly labeled system WIRING OVERVIEW, not checked KiCad schematics."""
from pathlib import Path
import subprocess,csv,json
R=Path(__file__).resolve().parents[1]
PINS=[
 ('SPOOL_STEP','ESP32 GPIO18','TMC2209 spool STEP','OUTPUT / 3.3V GPIO'),
 ('SPOOL_DIR','ESP32 GPIO19','TMC2209 spool DIR','OUTPUT / 3.3V GPIO'),
 ('TRAVERSE_STEP','ESP32 GPIO21','TMC2209 traverse STEP','OUTPUT / 3.3V GPIO'),
 ('TRAVERSE_DIR','ESP32 GPIO22','TMC2209 traverse DIR','OUTPUT / 3.3V GPIO'),
 ('DRIVER_ENABLE','ESP32 GPIO23','Both drivers EN (active low, board dependent)','OUTPUT / verify board variant'),
 ('TRAVERSE_HOME','ESP32 GPIO32','NC home switch -> GND, internal pull-up','HEALTHY low / OPEN high=>home or disconnect'),
 ('TRAVERSE_FAR','ESP32 GPIO33','NC far limit switch -> GND, internal pull-up','HEALTHY low / OPEN high=>limit or disconnect'),
 ('ESTOP_MONITOR','ESP32 GPIO25','Isolated read-only NC safety relay auxiliary','INPUT / independent motor cutoff required'),
 ('GUARD_MONITOR','ESP32 GPIO26','NC guard switch, standard; budget jumper must be reviewed','INPUT / active low'),
 ('HX711_DOUT','ESP32 GPIO34','HX711 DOUT with EXTERNAL electrical bias if needed','INPUT ONLY / standard'),
 ('HX711_CLK','ESP32 GPIO27','HX711 SCK','OUTPUT / standard'),
 ('ENCODER_A','ESP32 GPIO35','3.3 V compatible encoder A, external pull-up','INPUT ONLY / standard'),
 ('ENCODER_B','ESP32 GPIO39','3.3 V compatible encoder B, external pull-up','INPUT ONLY / standard'),
 ('USB_SERIAL','ESP32 USB','Programming and diagnostics','USB / independent logic power'),
]
for machine in ('budget-v1','standard-v1'):
 elec=R/machine/'electronics';elec.mkdir(parents=True,exist_ok=True)
 with (elec/'gpio_assignments.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['signal','controller','destination','note']);w.writerows(PINS)
 dot=r'''digraph System {
 graph [rankdir=LR, bgcolor="white", pad=0.25, nodesep=0.48, ranksep=0.72, label="CONCEPTUAL WIRING — NOT A QUALIFIED ELECTRICAL SCHEMATIC", labelloc=t, fontname="Helvetica", fontsize=16];
 node [shape=box, style="rounded,filled", fontname="Helvetica", color="#37647a", fillcolor="#e6f3f8", fontsize=11];
 edge [fontname="Helvetica", fontsize=10, color="#3b6576"];
 AC [label="AC mains\nQualified pre-assembled PSU only",fillcolor="#ffe4dc"];
 PSU [label="Listed isolated 24 V DC PSU\nvoltage + current rating TBD"];
 safety [label="Independent latching E-stop circuit\nrelay/contactor & fuse\nPOWER CUT on stop",fillcolor="#ffe0cf"];
 motorPower [label="Motor power distribution\n24 V DC via separate fuses"];
 driverA [label="TMC2209 module A\nSTEP/DIR/EN + VM/GND"];
 driverB [label="TMC2209 module B\nSTEP/DIR/EN + VM/GND"];
 motorA [label="NEMA17 take-up + belt drive"];
 motorB [label="NEMA17 traverse / T8"];
 controller [label="ESP32 DevKitC (3.3 V logic)\n5 V isolated USB or rated DC/DC",fillcolor="#dff1df"];
 home [label="NC Home + Far limit switches"];
 estop [label="NC safety auxiliary status\nmonitor only"];
 AC->PSU; PSU->safety[label="24V"]; safety->motorPower[label="24V MOTOR ONLY"]; motorPower->driverA;motorPower->driverB;
 driverA->motorA;driverB->motorB;
 controller->driverA[label="GPIO18/19/23\n3.3V logic"];controller->driverB[label="GPIO21/22/23\n3.3V logic"];
 home->controller[label="GPIO32/33"]; estop->controller[label="GPIO25 read-only"];
 safety->estop[style=dashed,label="aux status"];
 '''
 if machine=='standard-v1':
  dot+=r'''
 loadcell [label="Tension load cell -> HX711\nCALIBRATION REQUIRED"];
 encoder [label="Shaft encoder, external pull-ups\nPPR VALIDATION REQUIRED"];
 guard [label="Physical guard interlock -> safety circuit\nplus read-only GPIO26",fillcolor="#ffe0cf"];
 loadcell->controller[label="GPIO34 / GPIO27"];
 encoder->controller[label="GPIO35 / GPIO39"];
 guard->controller[label="GPIO26 monitor"];
 guard->safety[label="independent cutoff",color="#d45128"];
 '''
 else:
  dot+=r'''
 cover [label="Budget barrier / safety assessment\noperator safeguards PENDING",fillcolor="#ffe0cf"];
 cover->controller[label="GPIO26 / assigned NC input"];
 '''
 dot+='\n}\n'
 (elec/'concept_wiring.dot').write_text(dot)
 subprocess.run(['dot','-Tsvg',str(elec/'concept_wiring.dot'),'-o',str(elec/'concept_wiring.svg')],check=True)
 subprocess.run(['dot','-Tpng',str(elec/'concept_wiring.dot'),'-o',str(elec/'concept_wiring.png')],check=True)
 (elec/'README.md').write_text(f'''# {machine} — electrical engineering HOLD

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
''')
print('Electrical architecture diagrams exported.')
