"""Safety-first host state model and stepper/traverse motion *reference*.
Not a substitute for mechanical safety circuit, real-time ISR, or physical validation.
Copyright (c) 2026 Janus Rokkjær.
"""
from dataclasses import dataclass, field
from enum import Enum
import math

class State(str, Enum):
    UNHOMED='UNHOMED'; READY='READY'; RUNNING='RUNNING'; PAUSED='PAUSED'; FAULT='FAULT'; FINISHED='FINISHED'

@dataclass
class Config:
    core_mm: float = 90
    flange_max_mm: float = 150
    width_mm: float = 100
    fiber_mm: float = .25
    pitch_multiplier: float = 1.25
    radial_multiplier: float = 1.25
    target_m: float = 300
    surface_m_min: float = 2
    leadscrew_mm_per_rev: float = 8
    spool_steps_per_rev: int = 3200
    traverse_steps_per_rev: int = 3200
    tension_max_n: float | None = None  # MUST BE SET from product datasheet / evaluation
    tension_low_n: float | None = None

    def validate(self):
        values=(self.core_mm,self.flange_max_mm,self.width_mm,self.fiber_mm,self.pitch_multiplier,
                self.radial_multiplier,self.target_m,self.surface_m_min,self.leadscrew_mm_per_rev)
        if any(not math.isfinite(x) for x in values):raise ValueError('nonfinite motion configuration')
        if min(self.core_mm,self.width_mm,self.fiber_mm,self.target_m,self.surface_m_min,self.leadscrew_mm_per_rev)<=0:raise ValueError('positive inputs required')
        if self.flange_max_mm<=self.core_mm or self.pitch_multiplier<1 or self.radial_multiplier<1:raise ValueError('invalid spacing/flange')
        if self.spool_steps_per_rev<1 or self.traverse_steps_per_rev<1:raise ValueError('motor steps invalid')
        if self.tension_max_n is not None and (not math.isfinite(self.tension_max_n) or self.tension_max_n<=0):raise ValueError('tension max invalid')
        if self.tension_low_n is not None and (not math.isfinite(self.tension_low_n) or self.tension_low_n<0):raise ValueError('tension min invalid')
        if self.tension_max_n is not None and self.tension_low_n is not None and self.tension_low_n>=self.tension_max_n:raise ValueError('impossible tension band')
        return self

@dataclass
class Sensors:
    guard_closed: bool=True
    physical_estop_ok: bool=True
    home_active: bool=False
    end_active: bool=False
    tension_n: float | None=None
    encoder_ok: bool=True
    tension_sensor_ok: bool=True

@dataclass
class Model:
    config: Config
    standard: bool
    state: State=State.UNHOMED
    fault: str=''
    accumulated_m: float=0
    turns: float=0
    direction: int=1
    traverse_y_mm: float=0
    _low_seconds:float=0
    trace:list=field(default_factory=list)

    def __post_init__(self):self.config.validate()
    def _fault(self,reason):
        self.fault=reason;self.state=State.FAULT;self.trace.append(f'FAULT:{reason}')
    def home(self,sensors:Sensors):
        if self.state==State.RUNNING:raise RuntimeError('cannot home running machine')
        if not sensors.physical_estop_ok or not sensors.guard_closed:
            self._fault('safety chain open');return
        if not sensors.home_active:
            self._fault('traverse not physically home');return
        self.state=State.READY;self.traverse_y_mm=0;self.fault='';self.trace.append('READY')
    def start(self,sensors:Sensors):
        if self.state not in (State.READY,State.PAUSED):raise RuntimeError('not ready')
        if not sensors.guard_closed or not sensors.physical_estop_ok:self._fault('safety chain open');return
        if self.standard and (self.config.tension_max_n is None or self.config.tension_low_n is None):
            self._fault('standard tension limits uncalibrated');return
        if self.standard and (not sensors.tension_sensor_ok or sensors.tension_n is None or not sensors.encoder_ok):
            self._fault('required feedback unavailable');return
        self.state=State.RUNNING;self.trace.append('RUNNING')
    def pause(self):
        if self.state==State.RUNNING:self.state=State.PAUSED;self.trace.append('PAUSED')
    def stop(self):
        if self.state in (State.RUNNING,State.PAUSED):self.state=State.READY;self.trace.append('STOPPED')
    def run(self,dt_s:float,sensors:Sensors):
        if self.state!=State.RUNNING:return
        if dt_s<=0 or not math.isfinite(dt_s):raise ValueError('invalid time delta')
        if not sensors.physical_estop_ok or not sensors.guard_closed:self._fault('physical safety input open');return
        if sensors.end_active:self._fault('traverse end switch');return
        if self.standard:
            if not sensors.tension_sensor_ok or sensors.tension_n is None or not sensors.encoder_ok:
                self._fault('standard sensor disconnected');return
            if not math.isfinite(sensors.tension_n) or sensors.tension_n>self.config.tension_max_n:
                self._fault('tension overlimit');return
            if sensors.tension_n<self.config.tension_low_n:
                self._low_seconds+=dt_s
                if self._low_seconds>=1.0:self._fault('low tension / possible fiber break');return
            else:self._low_seconds=0
        c=self.config
        before=self.accumulated_m
        self.accumulated_m=min(c.target_m,self.accumulated_m+dt_s*c.surface_m_min/60)
        advance_m=self.accumulated_m-before
        if advance_m<0:return
        # integrate turns from current geometric radius, with layer step and traverse reversals
        width=max(0,c.width_mm-4)
        pitch=c.fiber_mm*c.pitch_multiplier
        radial=c.fiber_mm*c.radial_multiplier
        max_turns_per_layer=max(1,int(width/pitch))
        remaining=advance_m*1000
        while remaining>1e-7:
            layer=int(self.turns//max_turns_per_layer)
            r=c.core_mm/2+c.fiber_mm/2+layer*radial
            per_turn=math.hypot(2*math.pi*r,pitch)
            available=max_turns_per_layer-(self.turns%max_turns_per_layer)
            count=min(available,remaining/per_turn)
            self.turns+=count
            remaining-=count*per_turn
            if c.core_mm+2*(layer*radial+c.fiber_mm)>c.flange_max_mm:
                self._fault('maximum spool diameter reached');return
        layer=int(self.turns//max_turns_per_layer);fraction=(self.turns%max_turns_per_layer)*pitch
        self.direction=1 if layer%2==0 else -1
        self.traverse_y_mm=fraction if self.direction==1 else width-fraction
        if self.accumulated_m>=c.target_m-1e-9:self.state=State.FINISHED;self.trace.append('FINISHED')

    def reference_step_rates(self):
        c=self.config
        pitch=c.fiber_mm*c.pitch_multiplier
        layer=int(self.turns//max(1,int((c.width_mm-4)/pitch)))
        radius_mm=c.core_mm/2+c.fiber_mm/2+layer*c.fiber_mm*c.radial_multiplier
        rpm=(c.surface_m_min*1000)/(2*math.pi*radius_mm)
        spool_steps_s=rpm*c.spool_steps_per_rev/60
        trav_steps_s=spool_steps_s*(pitch/c.leadscrew_mm_per_rev)*(c.traverse_steps_per_rev/c.spool_steps_per_rev)
        return {'spindle_rpm':rpm,'spindle_step_hz':spool_steps_s,'traverse_step_hz':trav_steps_s,
                'direction':self.direction,'radius_mm':radius_mm}
