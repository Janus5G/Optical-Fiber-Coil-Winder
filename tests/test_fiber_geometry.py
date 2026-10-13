import pytest,math
from fiber import Spool,calculate

def test_standard_10km_coated_geometrically_fits():
 r=calculate(Spool(90,150,100,.25,1.25,1.25,2),10000)
 assert r['geometrically_fits'] and r['qualification']=='HOLD'
 assert r['capacity_m_geometric_upper_bound']>10000
 assert r['target_outer_diameter_mm']<=150

def test_standard_10km_buffered_does_not_fit():
 r=calculate(Spool(90,150,100,.9,1.25,1.25,2),10000)
 assert not r['geometrically_fits'] and r['qualification']=='HOLD'

def test_budget_300m_buffered_geom_fits():
 r=calculate(Spool(60,112,75,.9,1.25,1.25,2),300)
 assert r['geometrically_fits'] and r['target_outer_diameter_mm']<=112

def test_coated_fiber_bend_and_tension_uncertainty_is_explicit():
 r=calculate(Spool(90,150,100,.25),10000)
 assert r['bend_check_pass'] is None and r['tension_check_pass'] is None

def test_incorrect_bend_rejected():
 r=calculate(Spool(60,112,75,.9,manufacturer_min_bend_radius_mm=40),200)
 assert r['bend_check_pass'] is False and r['qualification']=='HOLD'

def test_tension_overlimit_rejected():
 r=calculate(Spool(90,150,100,.25,manufacturer_max_tension_n=.2,design_winding_tension_n=.3),200)
 assert r['tension_check_pass'] is False and r['qualification']=='HOLD'

@pytest.mark.parametrize('d,w,od,target',[(-1,100,150,10),(90,0,150,10),(90,100,80,10),(90,100,150,-1), (90,100,150,float('nan'))])
def test_bad_dimensions_fail(d,w,od,target):
 with pytest.raises(ValueError): calculate(Spool(d,od,w,.25),target)

def test_more_pitch_reduces_capacity():
 a=calculate(Spool(90,150,100,.25,1.10,1.10,2))
 b=calculate(Spool(90,150,100,.25,1.30,1.30,2))
 assert b['capacity_m_geometric_upper_bound']<a['capacity_m_geometric_upper_bound']

def test_negative_speed_rejected():
 with pytest.raises(ValueError):calculate(Spool(90,150,100,.25),100,-1)

def test_fiber_model_duration_calculated():
 r=calculate(Spool(90,150,100,.25),200,2)
 assert r['estimated_duration_min_at_constant_surface_speed']==100
