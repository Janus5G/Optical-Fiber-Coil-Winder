"""Unquoted planning-cost BOM. Never represent estimated amounts as supplier quotes."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1]
common=[
 ('CONTROLLER','ESP32-DevKitC V4 compatible ESP32-WROOM-32E board','controller',1,'3.3 V logic; verify GPIO map',75,'ESP32 board, no WROVER GPIO16/17 assumptions','board-specific pinout review'),
 ('MOTOR17','NEMA17 stepper 1.8 degree','take-up and traverse',2,'5 mm shaft; phase current selected for TMC2209 module',105,'42 mm NEMA17 frame','FIT/TORQUE THERMAL VALIDATION'),
 ('TMC','TMC2209 breakout with heatsink','stepper drivers',2,'24 V capable breakout; drive current derated',50,'verified breakout reference TBD','MODULE PINOUT/THERMAL VALIDATION'),
 ('PSU','Enclosed certified 24 V DC supply','motor power',1,'DIN enclosure-rated 24 V, power rating TBD',155,'licensed manufacturer to select','RATED PSU SELECTION'),
 ('BUCK','Rated DC/DC 24 V to 5 V logic converter','controller regulated power',1,'isolated or compatible module, fused',55,'specific module TBD','POWER INTEGRATION VALIDATION'),
 ('ESTOP','Latching red emergency stop mushroom','manual stopping switch',1,'normally closed positive opening rated component',75,'safety-class selection TBD','SAFETY ENGINEERING HOLD'),
 ('CONTACTOR','Hardwired motor energy cutoff/restart control','motor power interlock',1,'appropriately rated contactor/safety circuit to engineer',250,'specific fail-safe relay TBD','SAFETY ENGINEERING HOLD'),
 ('FUSE','DC fuse and holder assortment','power protection',1,'rated for protected branch and prospective fault current',55,'selection TBD','ELECTRICAL REVIEW'),
 ('LIMIT','Normally-closed mechanical limit switches','home and far traverse stop',2,'24 V-rated contacts / 3.3 V input interposed',24,'NC switch with bracket','FIT/ELECTRICAL REVIEW'),
 ('SHAFT','Metal Ø8 mm shaft stock','supply and takeup shaft',2,'cut to reel/frame, supported by bearings',52,'steel or compatible alloy','FIT/STRENGTH REVIEW'),
 ('BEARING','608-2RS or 608ZZ 8x22x7 mm bearing','spindle supports',4,'purchased bearing, not 3D printed',20,'608 series bearing','FIT/LOAD REVIEW'),
 ('BOLTS','M3/M4 fastener/washers/locknut kit','assembly',1,'adequate lengths verified per assembly',95,'commercial metric hardware','FIT REVIEW'),
 ('FIBERGUIDE','Polished ceramic eyelets/rollers','protect fiber coating',2,'supplier radius and surface spec TBD',46,'appropriate lapped ceramic part','FIBER CONTACT REVIEW'),
 ('TRAVERSE','T8 lead screw/nut, 2 guide rods and coupler','traverse mechanics',1,'8 mm nominal lead, >= required travel',200,'commercial linear kit','FIT/BACKLASH REVIEW'),
 ('DRIVE','Belt and two matching timing pulleys','spindle drive',1,'assume ratio 1:1 until measured; guarding required',100,'timing belt kit','DRIVE RATIO/FIT REVIEW'),
 ('BRAKE','Manual friction brake felt and spring','feed drag adjustment',1,'force torque characterized in test',48,'purchased compression spring/felt','TENSION SAFETY REVIEW'),
 ('DANCER','Dancer roller/bearing/spring kit','buffer tension transients',1,'low friction polished roller',85,'small non-abrading roller','DYNAMIC VERIFICATION'),
 ('WIRES','Wires/ferrules/screw terminals/strain relief','wiring',1,'proper insulation and cross-section TBD',90,'wiring kit','ELECTRICAL REVIEW'),
]
extras={
 'budget-v1':[
  ('BASE','Machinable plywood or alloy plate','420x180x10 mm bed',1,'420x180x10 mm with drilled holes',95,'plywood / suitable board','MECHANICAL REVIEW'),
  ('PRINT','3D print feed and takeup hubs, 13 part classes','nominal printed mechanisms',1,'tested PETG/PA preferred, print orientation TBD',150,'qualified service/own printer','LOAD/PRINT REVIEW'),
  ('GUARD','Budget operator barrier materials','hazard enclosure assessed separately',1,'exact cover and guard geometry TBD',80,'transparent barrier stock','GUARD DESIGN HOLD'),
 ],
 'standard-v1':[
  ('BASE','Aluminium/machinable rigid base plate','500x250x10 mm bed',1,'500x250x10 mm, suitable stiffness TBD',340,'aluminum plate','MECHANICAL REVIEW'),
  ('PRINT','3D-print part set, validated material TBD','nominal printed mechanisms',1,'printed prototypes + material characterization',250,'qualified service/own printer','LOAD/PRINT REVIEW'),
  ('GUARD','Transparent 3mm acrylic panels and hinge/access hardware','500x250x300 envelope',1,'impact/strength & clearance review',360,'clear PC preferred after risk assessment','GUARD/INTERLOCK HOLD'),
  ('GUARD_SW','Guard position switch rated for chosen circuit','guard interlock',1,'NC positive-opening or rated coded system TBD',110,'selected safety component','SAFETY ENGINEERING HOLD'),
  ('LOADCELL','Load cell 0-1kg class','fiber tension sensing',1,'accuracy/noise/range TBD; choose suitable dancer geometry',135,'selected load cell','FORCE CALIBRATION HOLD'),
  ('HX711','HX711 24-bit ADC amplifier module','load cell amplifier',1,'3.3V signal compatibility must be verified',40,'HX711 breakout','ELECTRICAL REVIEW'),
  ('ENCODER','Quadrature rotary encoder','take-up shaft angular position',1,'3.3V outputs + measured pulses/rev',175,'selected encoder and coupler','PPR/CALIBRATION HOLD'),
 ],
}
summary={}
for machine in extras:
 rows=[]
 for i,(part,desc,fn,qty,spec,price,alt,notes) in enumerate(common+extras[machine],start=1):
  rows.append({'id':f'{machine[0].upper()}-{i:03d}-{part}',
     'description':desc,'function':fn,'quantity':qty,'engineering_specification':spec,
     'example_component':desc,'acceptable_alternatives':alt,
     'unit_price_estimate_dkk':price,'extended_estimate_dkk':price*qty,
     'price_basis':'UNQUOTED PLANNING ALLOWANCE','price_date':'2026-10-13',
     'supplier_reference':'NOT VERIFIED','status':'ESTIMATE','fit_or_validation':notes})
 p=R/machine/'bom';p.mkdir(parents=True,exist_ok=True)
 with (p/'bom.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
 total=sum(item['extended_estimate_dkk'] for item in rows)
 summary[machine]={'line_items':len(rows),'budget_estimate_dkk':total,'cost_basis':'NOT QUOTED; EXCLUDES VAT/SHIPPING/TOOLS/FIBER/LABOUR','price_status':'ESTIMATE'}
 (p/'BOM_NOTES.md').write_text(f'''# {machine} material list — pricing status

All amounts are **engineering planning allowances**, not current retailer quotes; no supplier is confirmed. Prices dated 2026-10-13 solely for estimate bookkeeping. Component selection, electrical ratings, certifications, and fit are **HOLD**. Currency DKK. **Estimated subtotal: {total:,} DKK** excl. shipping, tax, labor, fiber, tools, reprints and measurement equipment.

Do not order parts based solely on this list; confirm exact model/dimensions, minimum order quantities, and in-country safety requirements. 3D-printed spindle drums must be assessed for hoop stress, creep, flange retention and dynamic balance.
''')
(R/'results'/'bom_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(summary)
