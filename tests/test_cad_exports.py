from pathlib import Path
import pytest,json,math
ROOT=Path(__file__).resolve().parents[1]

def test_cad_has_actual_files():
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 assert set(d)=={'budget-v1','standard-v1'}
 for name,manifest in d.items():
  assert len(manifest['files'])>=12
  for piece in manifest['files']:
   assert (ROOT/piece['stl']).stat().st_size>100
   assert (ROOT/piece['step']).stat().st_size>100

def test_cad_export_nominal_bounding_boxes():
 trimesh=pytest.importorskip('trimesh')
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 for _,info in d.items():
  for item in info['files']:
   mesh=trimesh.load(ROOT/item['stl'],force='mesh')
   assert len(mesh.vertices)>12,item['part']
   assert all(abs(a-b)<=.45 for a,b in zip(mesh.extents,item['nominal_bbox_mm'])),item['part']

def test_base_plate_export_dimensions():
 trimesh=pytest.importorskip('trimesh')
 for machine,expected in [('budget-v1',(420,180,10)),('standard-v1',(500,250,10))]:
  ext=trimesh.load(ROOT/machine/'cad'/'base_plate.stl').extents
  assert all(abs(a-b)<.15 for a,b in zip(ext,expected))

def test_spool_outer_diameter_not_greater_than_envelope():
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 for name,info in d.items():
  c=info['parameters_mm'];flange=next(x for x in info['files'] if x['part']=='flange')
  assert abs(flange['nominal_bbox_mm'][0]-c['flange_d'])<.1
  assert c['flange_d']<=c['max_od']

def test_assembly_nominal_envelope():
 cq=pytest.importorskip('cadquery')
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 for name,info in d.items():
  c=info['parameters_mm'];obj=cq.importers.importStep(str(ROOT/info['assembly_nominal_step'])).val();bb=obj.BoundingBox()
  assert bb.xmin>=-.001 and bb.xmax<=c['base_x']+.001
  assert bb.ymin>=-.001 and bb.ymax<=c['base_y']+.001
  assert bb.zmin>=-.001 and bb.zmax<=c['assembly_h']+.001

def test_nominal_parts_still_on_fit_hold():
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 assert all(q['status']=='FIT VERIFICATION REQUIRED' for info in d.values() for q in info['files'])

def test_drill_pattern_matches_base_manifest():
 ezdxf=pytest.importorskip('ezdxf')
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 for machine,data in d.items():
  drawing=ezdxf.readfile(str(ROOT/machine/'drawings/base_drill_pattern.dxf'))
  actual=[]
  for shape in drawing.modelspace().query('CIRCLE'):
   actual.append((round(shape.dxf.center.x,3),round(shape.dxf.center.y,3),round(shape.dxf.radius,3)))
  expected=[(round(p['x_mm'],3),round(p['y_mm'],3),round(p['radius_mm'],3)) for p in data['base_hole_manifest']]
  assert sorted(actual)==sorted(expected)

def test_base_drill_no_hole_overlap():
 d=json.loads((ROOT/'results'/'cad_manifest.json').read_text())
 for machine,data in d.items():
  points=data['base_hole_manifest']
  for idx,p in enumerate(points):
   for q in points[idx+1:]:
    assert math.hypot(p['x_mm']-q['x_mm'],p['y_mm']-q['y_mm'])>p['radius_mm']+q['radius_mm']+1
