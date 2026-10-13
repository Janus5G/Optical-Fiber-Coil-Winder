#!/usr/bin/env python3
"""Generates parametric, dimensional concept CAD, NOT fit-qualified manufacturing release.
No control of other repositories. CadQuery + ezdxf + matplotlib required for regeneration.
Copyright (c) 2026 Janus Rokkjær.
"""
from pathlib import Path
import sys, json, math
import cadquery as cq
from cadquery import exporters
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

R = Path(__file__).resolve().parents[1]
CFG = {
 'budget-v1': dict(base_x=420., base_y=180., base_t=10., assembly_h=165., supply_x=90., takeup_x=328., spindle_z=95., spindle_y=90., core_d=60., max_od=112., width=75., traverse_x=252., traverse_travel=80., flange_d=112., leadscrew_len=132.),
 'standard-v1':dict(base_x=500.,base_y=250.,base_t=10.,assembly_h=300.,supply_x=105.,takeup_x=380.,spindle_z=130.,spindle_y=125.,core_d=90.,max_od=150.,width=100.,traverse_x=301.,traverse_travel=120.,flange_d=150.,leadscrew_len=178.)
}

def cyl(radius, length, at, axis=(0,0,1)):
 return cq.Workplane().newObject([cq.Solid.makeCylinder(radius,length,cq.Vector(*at),cq.Vector(*axis))])

def bore(part, radius, length, at, axis=(0,0,1)):
 return part.cut(cyl(radius,length,at,axis))

def box(length,width,height,x,y,z):
 return cq.Workplane('XY').box(length,width,height).translate((x,y,z))

def mounting_holes(c):
 x,y=c['base_x'],c['base_y'];holes=[]
 for spindle in (c['supply_x'],c['takeup_x']):
  for dx in (-15,15):
   for yy in (12,y-12):holes.append((spindle+dx,yy,2.25,'bearing_block'))
 sy1=(y-c['traverse_travel'])/2-10
 sy2=(y+c['traverse_travel'])/2+10
 for xx in (c['traverse_x']-16,c['traverse_x']+16):
  for yy in (sy1,sy2):holes.append((xx,yy,2.25,'traverse_rail_support'))
 for dx in (-21,21):holes.append((c['takeup_x']+42+dx,y-37,2.25,'nema17_mount'))
 for dx in (-14,14):holes.append((c['supply_x']+70+dx,c['spindle_y'],2.25,'dancer_pivot'))
 holes.append((c['supply_x']-34,y-25,2.2,'brake_mount'))
 for dx in (-30,30):
  for dy in (-18,18):holes.append((x/2+dx,26+dy,1.65,'controller_bracket'))
 if c['assembly_h']>=300:
  for dx in (-10,10):holes.append((x-40+dx,12,2.25,'guard_switch_mount'))
 for xx in (15,x-15):
  for yy in (15,y-15):holes.append((xx,yy,3.,'base_to_bench'))
 return holes

def base(c):
 x,y,t=c['base_x'],c['base_y'],c['base_t']
 p=box(x,y,t,x/2,y/2,t/2)
 for px,py,rad,_label in mounting_holes(c):
  p=bore(p,rad,t+2,(px,py,-1))
 return p

def spool_core(c):
 # Printable radial-rib drum with a 4 mm shell and a reinforced Ø18 mm shaft hub.
 # It is a nominal one-piece print, subject to printer/material and load tests.
 d,w=c['core_d'],c['width'];outer=d/2
 p=cyl(outer,w,(0,-w/2,0),(0,1,0))
 p=bore(p,outer-4,w+2,(0,-w/2-1,0),(0,1,0))
 hub=cyl(9,w,(0,-w/2,0),(0,1,0))
 for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
  span=outer-4-8
  if dx:
   web=box(span,w,6,dx*(8+span/2),0,0)
  else:
   web=box(6,w,span,0,0,dz*(8+span/2))
  hub=hub.union(web)
 p=p.union(hub)
 p=bore(p,4.1,w+2,(0,-w/2-1,0),(0,1,0))
 # four through clearances in radial ribs for removable flanges
 for xx,zz in ((12,0),(-12,0),(0,12),(0,-12)):
  p=bore(p,1.65,w+2,(xx,-w/2-1,zz),(0,1,0))
 return p

def flange(c):
 d=c['flange_d']; p=cyl(d/2,4,(0,0,0),(0,1,0)); p=bore(p,4.1,6,(0,-1,0),(0,1,0))
 for xx,zz in ((12,0),(-12,0),(0,12),(0,-12)):
  p=bore(p,1.65,6,(xx,-1,zz),(0,1,0))
 return p

def bearing_block(c):
 # 608ZZ nominal Ø22×7, body fixed with M4 holes. Nominal clearance 22.2 -> FIT HOLD.
 p=box(38,18,41,0,0,20.5)
 p=bore(p,11.1,20,(0,-10,25),(0,1,0))
 for x in (-15,15):p=bore(p,2.25,12,(x,0,-1))
 return p

def motor_mount(c):
 # NEMA17 mounting holes 31 mm nominal spacing, 22.4 mm centre boss cutout.
 p=box(54,38,5,0,0,2.5).union(box(54,5,53,0,16.5,26.5))
 for x in (-15.5,15.5):
  for z in (20.5-15.5,20.5+15.5):
   p=bore(p,1.75,7,(x,13,z),(0,1,0))
 p=bore(p,11.2,7,(0,13,20.5),(0,1,0))
 for x in (-21,21):p=bore(p,2.25,7,(x,-5,-1))
 return p

def rail_support(c):
 p=box(44,20,45,0,0,22.5)
 p=bore(p,4.1,22,(0,-11,29),(0,1,0))
 p=bore(p,2.5,22,(17,-11,31),(0,1,0))
 p=bore(p,2.5,22,(-17,-11,31),(0,1,0))
 for x in (-16,16):p=bore(p,2.25,47,(x,0,-1))
 return p

def slider(c):
 p=box(48,24,24,0,0,0)
 for xx in (-17,17):p=bore(p,2.65,26,(xx,-13,0),(0,1,0))
 # anti-backlash nut mount, nominal 8 mm leadscrew *not a functioning nut geometry*
 p=bore(p,4.5,26,(0,-13,0),(0,1,0))
 for xx in (-9,9):p=bore(p,1.65,26,(xx,-13,-6),(0,1,0))
 return p

def ceramic_guide_mount(c):
 p=box(38,22,35,0,0,17.5)
 p=bore(p,3.3,24,(0,-12,25),(0,1,0))  # Ø6.6 ceramic eyelet seat, verify tolerance
 for x in (-13,13):p=bore(p,2.25,38,(x,0,-1))
 return p

def dancer_pivot(c):
 p=box(42,32,28,0,0,14)
 p=bore(p,3.1,34,(0,-17,17),(0,1,0))
 for x in (-14,14):p=bore(p,2.25,30,(x,0,-1))
 return p

def dancer_arm(c):
 p=box(100,14,7,50,0,0)
 p=bore(p,3.1,16,(12,-8,0),(0,1,0))
 p=bore(p,3.1,16,(90,-8,0),(0,1,0))
 return p

def felt_brake_mount(c):
 p=box(28,24,34,0,0,17)
 p=bore(p,4.15,26,(0,-13,23),(0,1,0))
 p=bore(p,2.2,36,(0,0,-1))
 return p

def electronics_bracket(c):
 p=box(74,52,3,0,0,1.5)
 for xx in (-30,30):
  for yy in (-18,18):p=bore(p,1.65,5,(xx,yy,-1))
 return p

def safety_switch_mount(c):
 p=box(32,28,4,0,0,2).union(box(32,4,35,0,12,17.5))
 for xx in (-10,10):
  p=bore(p,1.65,6,(xx,10,24),(0,1,0))
  p=bore(p,2.25,6,(xx,-6,-1))
 return p

def panel(x,y,z,thickness=3):
 return box(x,y,z,0,0,0)

def source_assembly(c):
 # Reference rods, purchased hardware, acrylic panels; no claimed functional alignment.
 w=c['width']; y=c['spindle_y'];z=c['spindle_z']; d=c['flange_d']
 parts={
  'base_plate':(base(c),(0,0,0)),
  'spool_core':(spool_core(c),(0,0,0)),
  'flange':(flange(c),(0,0,0)),
  'bearing_block':(bearing_block(c),(0,0,0)),
  'nema17_mount':(motor_mount(c),(0,0,0)),
  'traverse_rail_support':(rail_support(c),(0,0,0)),
  'traverse_slider':(slider(c),(0,0,0)),
  'ceramic_eyelet_mount':(ceramic_guide_mount(c),(0,0,0)),
  'dancer_pivot':(dancer_pivot(c),(0,0,0)),
  'dancer_arm':(dancer_arm(c),(0,0,0)),
  'brake_mount':(felt_brake_mount(c),(0,0,0)),
  'controller_bracket':(electronics_bracket(c),(0,0,0)),
  'guard_switch_mount':(safety_switch_mount(c),(0,0,0)),
 }
 return parts

def assembly(c, parts):
 y,z,w=c['spindle_y'],c['spindle_z'],c['width']; items=[]
 def put(name, off):items.append((name,parts[name][0].translate(off)))
 put('base_plate',(0,0,0))
 for x in (c['supply_x'],c['takeup_x']):
  put('spool_core',(x,y,z))
  put('flange',(x,y-w/2-4,z));put('flange',(x,y+w/2,z))
  for end_y in (12,c['base_y']-12):
   put('bearing_block',(x,end_y,z-25))
 put('nema17_mount',(c['takeup_x']+42,c['base_y']-32,10))
 ty=c['traverse_x'];sup1=(c['base_y']-c['traverse_travel'])/2-10;sup2=(c['base_y']+c['traverse_travel'])/2+10
 for sy in (sup1,sup2):put('traverse_rail_support',(ty,sy,12))
 put('traverse_slider',(ty,y,41));put('ceramic_eyelet_mount',(ty,y,58))
 put('dancer_pivot',(c['supply_x']+70,y,10))
 put('dancer_arm',(c['supply_x']+70,y,z+15))
 put('brake_mount',(c['supply_x']-34,c['base_y']-25,10))
 put('controller_bracket',(c['base_x']/2,26,10))
 if c['assembly_h']>=300:put('guard_switch_mount',(c['base_x']-40,18,10))
 # nominal metallic bought spindle rods - reference-only axis cylinders
 for x in (c['supply_x'],c['takeup_x']):
  items.append(('8mm_reference_shaft',cyl(4,c['base_y']-8,(x,4,z),(0,1,0))))
 # traverse 8mm lead screw + two 5mm rail rods - nominal references
 items.append(('T8_reference_leadscrew',cyl(4,c['leadscrew_len'],(ty,sup1,41),(0,1,0))))
 for dx in (-17,17):items.append(('linear_rail_reference',cyl(2.5,c['leadscrew_len'],(ty+dx,sup1,41),(0,1,0))))
 if c['assembly_h']>=300:
  h=c['assembly_h']-13; bx=c['base_x'];by=c['base_y']
  items+= [('acrylic_left_guard',box(3,by,h,1.5,by/2,10+h/2)),
           ('acrylic_right_guard',box(3,by,h,bx-1.5,by/2,10+h/2)),
           ('acrylic_rear_guard',box(bx,3,h,bx/2,by-1.5,10+h/2)),
           ('acrylic_front_guard',box(bx,3,h,bx/2,1.5,10+h/2)),
           ('acrylic_top_guard',box(bx,by,3,bx/2,by/2,10+h+1.5))]
 return items

def make_dxf(c, path):
 d=ezdxf.new();m=d.modelspace(); x,y=c['base_x'],c['base_y']
 m.add_lwpolyline([(0,0),(x,0),(x,y),(0,y),(0,0)])
 for xx,yy,r,desc in mounting_holes(c):
  m.add_circle((xx,yy),r)
 d.saveas(path)

def drawing(c,where,machine,view='top'):
 x,y=c['base_x'],c['base_y']
 fig,ax=plt.subplots(figsize=(12,6.6))
 if view=='top':
  ax.add_patch(Rectangle((0,0),x,y,fill=False,lw=2,ec='#172938'))
  for loc,name in [(c['supply_x'],'SUPPLY SHAFT'),(c['takeup_x'],'TAKE-UP SHAFT')]:
   d=c['flange_d'];w=c['width']
   ax.add_patch(Rectangle((loc-d/2,c['spindle_y']-w/2-4),d,w+8,
                          ec='#277fa4',fc='#d5eef7',alpha=.65,lw=1.8))
   ax.plot([loc,loc],[c['spindle_y']-w/2-10,c['spindle_y']+w/2+10],color='#377e9f',ls='--')
   ax.text(loc,c['spindle_y'],name,ha='center',va='center',weight='bold',fontsize=9)
  ax.add_patch(Rectangle((c['traverse_x']-6,(y-c['traverse_travel'])/2),12,c['traverse_travel'],
                         ec='#a44a20',fc='#ffe0b9',alpha=.8))
  ax.text(c['traverse_x']+12,c['spindle_y'],'TRAVERSE AXIS',rotation=90,va='center',fontsize=8)
  ax.add_patch(Circle((c['supply_x']+70,c['spindle_y']),6,fc='#9f9988'))
  ax.set_xlim(-25,x+20);ax.set_ylim(-30,y+40);ax.set_aspect('equal');ax.axis('off')
  ax.annotate('',xy=(0,-15),xytext=(x,-15),arrowprops={'arrowstyle':'<->','color':'black'})
  ax.text(x/2,-24,f'{x:.0f} mm',ha='center',va='center')
  ax.annotate('',xy=(-15,0),xytext=(-15,y),arrowprops={'arrowstyle':'<->','color':'black'})
  ax.text(-23,y/2,f'{y:.0f} mm',rotation=90,ha='center')
  ax.text(x/2,y+20,f'{machine.upper()} — PLAN VIEW (X / Y)',weight='bold',ha='center',fontsize=12)
  ax.text(x/2,y+4,'Rectangles = spool swept radius in X and axial width in Y (not photographs)',ha='center',fontsize=8)
 else:
  h=c['assembly_h'];z=c['spindle_z']
  ax.add_patch(Rectangle((0,0),x,10,ec='#273c4d',fc='#b5cbd5'))
  for loc,name in [(c['supply_x'],'SUPPLY'),(c['takeup_x'],'TAKE-UP')]:
   ax.add_patch(Circle((loc,z),c['flange_d']/2,ec='#297ea5',fc='#d8eef7',alpha=.7,lw=2))
   ax.add_patch(Circle((loc,z),c['core_d']/2,ec='#6c9bb0',fc='none',ls='--',lw=1.4))
   ax.plot(loc,z,'o',color='#17445b',markersize=5)
   ax.text(loc,z,name,ha='center',va='center',weight='bold',fontsize=10)
  ax.add_patch(Circle((c['supply_x']+70,z+17),8,ec='#a18063',fc='#d5b89a'))
  if h>=300:
   ax.add_patch(Rectangle((0,0),x,h,fill=False,lw=2,ls='--',ec='#739dad'))
  ax.set_xlim(-28,x+25);ax.set_ylim(-18,h+33);ax.set_aspect('equal');ax.axis('off')
  ax.annotate('',xy=(-15,0),xytext=(-15,h),arrowprops={'arrowstyle':'<->','color':'black'})
  ax.text(-25,h/2,f'{h:.0f} mm limit',rotation=90,va='center',ha='center')
  ax.text(x/2,h+18,f'{machine.upper()} — FRONT ELEVATION (X / Z)',weight='bold',ha='center',fontsize=12)
  ax.text(x/2,h+4,'Circles = spindle flange and core profiles; nominal geometry / fit verification HOLD',ha='center',fontsize=8)
 fig.savefig(where,dpi=150,bbox_inches='tight');plt.close(fig)

def main():
 record={}
 for machine,c in CFG.items():
  cad=R/machine/'cad';draw=R/machine/'drawings';cad.mkdir(parents=True,exist_ok=True);draw.mkdir(parents=True,exist_ok=True)
  partlist=source_assembly(c)
  stat=[]
  for name,(shape,_) in partlist.items():
   # STEP source for purchased-reference shapes not included (CAD parts actual geometry only)
   stp=cad/(name+'.step');stl=cad/(name+'.stl')
   exporters.export(shape,str(stp));exporters.export(shape,str(stl),tolerance=0.18,angularTolerance=0.25)
   bb=cq.importers.importStep(str(stp)).val().BoundingBox()  # actual STEP geometry, not triangulated BRep tolerance
   stat.append({'part':name,'step':str(stp.relative_to(R)),'stl':str(stl.relative_to(R)),
       'nominal_bbox_mm':[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)],
       'status':'FIT VERIFICATION REQUIRED'})
  assembly_items=assembly(c,partlist)
  combined=cq.Compound.makeCompound([s.val() for _,s in assembly_items]);exporters.export(combined,str(cad/'assembly_nominal.step'))
  make_dxf(c,draw/'base_drill_pattern.dxf')
  drawing(c,draw/'nominal_top_view.png',machine,'top')
  drawing(c,draw/'nominal_front_elevation.png',machine,'front')
  # face plate for electronics as 2d SVG vector
  w=c['base_x'];h=c['base_y'];(draw/'base_outline.svg').write_text(
   f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}"><rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" fill="none" stroke="black" stroke-width="1"/></svg>\n')
  record[machine]={'parameters_mm':c,'files':stat,'assembly_nominal_step':str((cad/'assembly_nominal.step').relative_to(R)),
                    'base_hole_manifest':[{'x_mm':a,'y_mm':b,'radius_mm':r,'for_part':purpose} for a,b,r,purpose in mounting_holes(c)],'reference_notes':'Metal shafts, bearings, motor, drives, pulley/belt, ceramic inserts and standard guard interlock need procurement-specific verification'}
 (R/'results'/'cad_manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 print('Created parametric CAD: ',sum(len(v['files']) for v in record.values()),'distinct exported parts')

if __name__=='__main__':main()
