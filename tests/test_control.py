import pytest,math
from control import Model,Config,Sensors,State

def mk_standard():
 return Model(Config(target_m=2,tension_max_n=.5,tension_low_n=.02),True)

def test_machine_homing():
 m=mk_standard();m.home(Sensors(home_active=True,tension_n=.1));assert m.state==State.READY

def test_cannot_start_without_home():
 m=mk_standard()
 with pytest.raises(RuntimeError):m.start(Sensors(tension_n=.1))

def test_requires_limit_sensor_for_home():
 m=mk_standard();m.home(Sensors(home_active=False,tension_n=.1));assert m.state==State.FAULT

def test_standard_fails_without_sensor_feedback():
 m=mk_standard();m.home(Sensors(home_active=True));m.start(Sensors(tension_n=None))
 assert m.state==State.FAULT

def test_standard_fails_without_tension_limits():
 m=Model(Config(),True);m.home(Sensors(home_active=True));m.start(Sensors(tension_n=.1));assert m.state==State.FAULT

def test_max_tension_fail_closed():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(.1,Sensors(tension_n=.6));assert m.state==State.FAULT

def test_break_detection_low_tension():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(.6,Sensors(tension_n=0.0));assert m.state==State.RUNNING
 m.run(.5,Sensors(tension_n=0.0));assert m.state==State.FAULT

def test_encoder_loss_fault():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(.1,Sensors(tension_n=.1,encoder_ok=False));assert m.state==State.FAULT

def test_endstop_fault():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(.1,Sensors(tension_n=.1,end_active=True));assert m.state==State.FAULT

def test_estop_fault():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(.1,Sensors(tension_n=.1,physical_estop_ok=False));assert m.state==State.FAULT

def test_guard_open_fault():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(.1,Sensors(tension_n=.1,guard_closed=False));assert m.state==State.FAULT

def test_pause_and_stop():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.pause();assert m.state==State.PAUSED
 m.stop();assert m.state==State.READY

def test_finishes_2m():
 m=mk_standard();s=Sensors(home_active=True,tension_n=.1);m.home(s);m.start(s)
 m.run(60,s);assert m.state==State.FINISHED and m.accumulated_m==2

def test_speed_and_traverse_reference_is_consistent():
 m=mk_standard();rates=m.reference_step_rates();c=m.config
 expected=rates['spindle_step_hz']*(c.fiber_mm*c.pitch_multiplier/c.leadscrew_mm_per_rev)
 assert math.isclose(rates['traverse_step_hz'],expected,rel_tol=1e-7)

def test_budget_simpler_feedback_allowed():
 m=Model(Config(target_m=1,core_mm=60,flange_max_mm=112,width_mm=75,fiber_mm=.9),False)
 s=Sensors(home_active=True);m.home(s);m.start(s);m.run(10,s)
 assert m.state==State.RUNNING and m.accumulated_m>0

def test_invalid_settings_rejected():
 with pytest.raises(ValueError):Model(Config(fiber_mm=-1),False)
