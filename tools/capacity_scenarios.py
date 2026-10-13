"""Reproducible geometry-only scenarios; intended fiber length is NOT proof of build viability."""
from pathlib import Path
import sys, json, csv
r = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(r / 'common' / 'fiber-calculations'))
from fiber import Spool, calculate
scenarios = [
 ('budget-v1', 60, 112, 75),
 ('standard-v1', 90, 150, 100),
 ('standard-v1-alternative_60mm_core',60,150,100),
]
fibers = [('coated_geometry_only', .25),('buffered_geometry_only', .9),('jacketed_2mm_geometry_only', 2.0)]
rows=[]
for machine,core,outer,width in scenarios:
 for label,dia in fibers:
  for target in (200,300,2000,10000):
   r0=calculate(Spool(core,outer,width,dia,pitch_factor=1.25,radial_factor=1.25,side_margin_mm=2),target)
   rows.append({'machine':machine,'core_mm':core,'max_od_mm':outer,'winding_width_mm':width,
                'fiber_class':label,'fiber_od_mm':dia,'target_m':target,
                'geometric_upper_estimate_m':r0['capacity_m_geometric_upper_bound'],
                'geometric_fit':r0['geometrically_fits'],
                'physically_qualified':False,'status':'HOLD - product bend/tension/optical verification'})
(r/'results'/'capacity_scenarios.json').write_text(json.dumps(rows,indent=2)+'\n')
with (r/'results'/'capacity_scenarios.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
print('Generated ',len(rows),'geometry-only outcomes')
