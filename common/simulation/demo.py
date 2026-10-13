"""Offline demonstration; synthetic inputs only, no physical measurements."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'common'/'controller'))
from control import Model,Config,Sensors

def simulate(standard=True):
 cfg=Config(target_m=2.0, tension_max_n=.5, tension_low_n=.02)
 m=Model(cfg,standard=standard)
 s=Sensors(home_active=True,tension_n=.1)
 m.home(s);m.start(s)
 for step in range(120):
  m.run(1.,s)
  if m.state.value!='RUNNING':break
 return {'kind':'SYNTHETIC_HOST_SIMULATION','state':m.state.value,'meters':m.accumulated_m,
         'turns':m.turns,'traverse_mm':m.traverse_y_mm,'trace':m.trace,'motor_reference':m.reference_step_rates()}

if __name__=='__main__':
 d=simulate();(R/'results'/'host_simulation.json').write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps(d,indent=2))
