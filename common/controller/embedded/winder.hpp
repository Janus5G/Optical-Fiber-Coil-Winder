// Optical Fiber Coil Winder prototype control for ESP32 Arduino.
// MOTION IS BUILD-LOCKED until independent physical safety verification.
// Copyright (c) 2026 Janus Rokkjær. License under review.
#pragma once
#include <Arduino.h>
#include <Preferences.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef STANDARD_MACHINE
#define STANDARD_MACHINE 0
#endif
#ifndef ENABLE_REAL_MOTION
#define ENABLE_REAL_MOTION 0
#endif

namespace winder {
constexpr int STEP_PIN=18, DIR_PIN=19, TRAVERSE_STEP=21, TRAVERSE_DIR=22, ENABLE_PIN=23;
constexpr int HOME_PIN=32, FAR_PIN=33, ESTOP_MONITOR_PIN=25, GUARD_PIN=26;
constexpr int HX_DOUT=34, HX_SCK=27, ENC_A=35, ENC_B=39;
constexpr float LEAD_MM_REV=8.0f;
constexpr uint32_t MICROSTEPS_REV=3200;
constexpr unsigned PULSE_MICROS=4;
constexpr unsigned long HOME_TIMEOUT_MS=10000;
// WARNING: HX711 scale and encoder PPR must be established by physical calibration.
// External E-stop contactor must remove motor power regardless of MCU/software state.

enum State : uint8_t { DISABLED, UNHOMED, HOMING, READY, RUNNING, PAUSED, FINISHED, FAULT };
inline const char* stateName(State s) {
 switch(s) {case DISABLED:return "DISABLED";case UNHOMED:return "UNHOMED";
 case HOMING:return "HOMING";case READY:return "READY";case RUNNING:return "RUNNING";
 case PAUSED:return "PAUSED";case FINISHED:return "FINISHED";default:return "FAULT";}
}

struct Settings {
 float core_mm=STANDARD_MACHINE?90.0f:60.0f;
 float outer_mm=STANDARD_MACHINE?150.0f:112.0f;
 float width_mm=STANDARD_MACHINE?100.0f:75.0f;
 float fiber_mm=STANDARD_MACHINE?0.25f:0.9f;
 float pitch_factor=1.25f;
 float radial_factor=1.25f;
 float target_m=STANDARD_MACHINE?10000.0f:300.0f;
 float speed_m_min=2.0f;
 float loadcell_newtons_per_count=0.0f; // required, cannot infer
 float tension_limit_n=0.0f; // required, specific to fiber product
 float tension_setpoint_n=0.0f;
 float min_tension_n=0.0f;
 uint32_t encoder_ppr=0; // required STANDARD, real PPR and wiring must be verified
 bool sane() const {
  return isfinite(core_mm)&&isfinite(outer_mm)&&isfinite(width_mm)&&isfinite(fiber_mm)&&
     isfinite(pitch_factor)&&isfinite(radial_factor)&&isfinite(target_m)&&isfinite(speed_m_min)&&
     core_mm>=20 && outer_mm>core_mm && outer_mm<=150 && width_mm>=10 && width_mm<=100 &&
     fiber_mm>=.2f && fiber_mm<=3.f && pitch_factor>=1.f && radial_factor>=1.f &&
     target_m>0 && target_m<=10000 && speed_m_min>.01f && speed_m_min<=5.f;
 }
};

class Winder {
 Preferences prefs;
 Settings cfg;
 State state=ENABLE_REAL_MOTION?UNHOMED:DISABLED;
 String err="";
 uint32_t lastPulseAt=0, lastUpdate=0, homingStarted=0, lastEncoderCheck=0;
 uint32_t stepCounter=0, layer=0, turnsInLayer=0, lowTensionAt=0;
 uint32_t encoderBaseline=0, stepBaseline=0;
 float tensionControlMultiplier=1.0f;
 float meters=0, traverseResidual=0, currentHz=0;
 int8_t traverseDirection=1;
 int32_t hxOffset=0;
 volatile uint32_t encoderCount=0;
 static Winder* active;
 static void IRAM_ATTR encoderInterrupt() { if(active)active->encoderCount++; }

 bool safeInputs() const {return digitalRead(ESTOP_MONITOR_PIN)==LOW && digitalRead(GUARD_PIN)==LOW;}
 void disable() {digitalWrite(ENABLE_PIN,HIGH);currentHz=0;}
 void fault(const char* why){err=why;state=FAULT;disable();Serial.printf("FAULT %s\n",why);}
 bool hxRead(int32_t &value){
  if(digitalRead(HX_DOUT)==HIGH)return false;
  uint32_t v=0;
  noInterrupts();
  for(int i=0;i<24;i++){
   digitalWrite(HX_SCK,HIGH);delayMicroseconds(1);v=(v<<1)|digitalRead(HX_DOUT);
   digitalWrite(HX_SCK,LOW);delayMicroseconds(1);
  }
  digitalWrite(HX_SCK,HIGH);delayMicroseconds(1);digitalWrite(HX_SCK,LOW);
  interrupts();
  if(v&0x800000)v|=0xff000000;
  value=(int32_t)v;return true;
 }
 float pitch() const {return cfg.fiber_mm*cfg.pitch_factor;}
 uint32_t turnsPerLayer() const {return max(1UL,(uint32_t)floorf((cfg.width_mm-4.f)/pitch()));}
 float centerRadius(){return cfg.core_mm/2.f+cfg.fiber_mm/2.f+layer*cfg.fiber_mm*cfg.radial_factor;}
 float spindleTargetHz(){return cfg.speed_m_min*1000.f/(2.f*PI*centerRadius())*MICROSTEPS_REV/60.f;}
 void stepPin(int pin){digitalWrite(pin,HIGH);delayMicroseconds(PULSE_MICROS);digitalWrite(pin,LOW);}
 void spoolStep(){
  stepPin(STEP_PIN);stepCounter++;
  meters+=hypotf(2.f*PI*centerRadius(),pitch())/(1000.f*MICROSTEPS_REV);
  traverseResidual+=(pitch()/LEAD_MM_REV); // ratio assumes same full rev steps on both axes
  if(traverseResidual>=1.f){traverseResidual-=1.f;stepPin(TRAVERSE_STEP);}
  if(stepCounter%MICROSTEPS_REV==0){
   turnsInLayer++;
   if(turnsInLayer>=turnsPerLayer()){
    turnsInLayer=0;layer++;
    traverseDirection=-traverseDirection;
    digitalWrite(TRAVERSE_DIR,traverseDirection>0?HIGH:LOW);
   }
  }
  if(cfg.core_mm+cfg.fiber_mm+2.f*layer*cfg.fiber_mm*cfg.radial_factor>cfg.outer_mm){fault("OUTER_DIAMETER");return;}
  if(meters>=cfg.target_m){state=FINISHED;disable();Serial.printf("FINISHED %.3f meters (ESTIMATE)\n",meters);}
 }
 void save(){prefs.begin("winder",false);prefs.putBytes("cfg",&cfg,sizeof(cfg));prefs.end();}
 void load(){
  prefs.begin("winder",true);
  if(prefs.getBytesLength("cfg")==sizeof(cfg)){
   Settings candidate;
   if(prefs.getBytes("cfg",&candidate,sizeof(candidate))==sizeof(candidate)&&candidate.sane())cfg=candidate;
  }
  prefs.end();
 }
 void status(){Serial.printf("STATE=%s M=%.4f LAYER=%lu ERR=%s ESTOP=%d GUARD=%d\n",
   stateName(state),meters,(unsigned long)layer,err.c_str(),digitalRead(ESTOP_MONITOR_PIN),digitalRead(GUARD_PIN));}
 void command(String s){
  s.trim();s.toUpperCase();
  if(s=="STATUS"){status();return;}
  if(s=="STOP"){state=UNHOMED;disable();Serial.println("STOPPED / RE-HOME REQUIRED");return;}
  if(s=="PAUSE"&&state==RUNNING){state=PAUSED;disable();Serial.println("PAUSED");return;}
  if(s=="HOME"){
   if(!ENABLE_REAL_MOTION){Serial.println("BLOCKED SAFETY_BUILD_LOCK");return;}
   if(!safeInputs() || digitalRead(FAR_PIN)==HIGH){fault("SAFETY_OR_TRAVERSE_LIMIT");return;}
   if(state==RUNNING||state==HOMING){Serial.println("BUSY");return;}
   state=HOMING;homingStarted=millis();lastPulseAt=micros();
   digitalWrite(TRAVERSE_DIR,LOW);digitalWrite(ENABLE_PIN,LOW);Serial.println("HOMING");return;
  }
  if(s=="START"){
   if(!ENABLE_REAL_MOTION){Serial.println("BLOCKED SAFETY_BUILD_LOCK");return;}
   if(state!=READY&&state!=PAUSED){Serial.println("BLOCKED NOT_READY");return;}
   if(!safeInputs()){fault("SAFETY_CHAIN");return;}
   if(STANDARD_MACHINE && (!(cfg.loadcell_newtons_per_count>0) || !(cfg.tension_limit_n>0) || !(cfg.tension_setpoint_n>cfg.min_tension_n) || !(cfg.tension_setpoint_n<cfg.tension_limit_n) || cfg.encoder_ppr==0)){
    fault("STANDARD_NOT_CALIBRATED");return;
   }
   currentHz=0;lastUpdate=micros();lastPulseAt=micros();state=RUNNING;
   encoderBaseline=encoderCount;stepBaseline=stepCounter;tensionControlMultiplier=1.0f;
   digitalWrite(ENABLE_PIN,LOW);Serial.println("RUNNING");return;
  }
  if(s=="TARE" && state!=RUNNING && state!=HOMING){
   int32_t raw=0;if(hxRead(raw)){hxOffset=raw;Serial.println("TARE SET (VOLATILE)");}
   else Serial.println("TARE FAILED SENSOR NOT READY");return;
  }
  if(s.startsWith("CAL_LOAD ") && state!=RUNNING){
   float scale,low,target,maxN;
   if(sscanf(s.c_str(),"CAL_LOAD %f %f %f %f",&scale,&low,&target,&maxN)!=4 ||
      !isfinite(scale)||!isfinite(low)||!isfinite(target)||!isfinite(maxN)||
      scale<=0||low<0||target<=low||maxN<=target){Serial.println("INVALID CAL_LOAD");return;}
   cfg.loadcell_newtons_per_count=scale;cfg.min_tension_n=low;
   cfg.tension_setpoint_n=target;cfg.tension_limit_n=maxN;save();
   Serial.println("LOAD SENSOR PARAMETERS STORED - PHYSICAL CALIBRATION STILL REQUIRED");return;
  }
  if(s.startsWith("CAL_ENCODER ") && state!=RUNNING){
   long p=s.substring(12).toInt();
   if(p<1 || p>200000){Serial.println("INVALID PPR");return;}
   cfg.encoder_ppr=(uint32_t)p;save();Serial.println("PPR STORED - VERIFY ENCODER DIRECTION AND PULSE IN PHYSICAL TEST");return;
  }
  if(s.startsWith("TARGET ")){
   float x=s.substring(7).toFloat();Settings t=cfg;t.target_m=x;
   if(state==RUNNING||!t.sane()){Serial.println("INVALID OR BUSY");return;}
   cfg=t;save();Serial.printf("TARGET %.2f m\n",cfg.target_m);return;
  }
  if(s.startsWith("SPEED ")){
   float x=s.substring(6).toFloat();Settings t=cfg;t.speed_m_min=x;
   if(state==RUNNING||!t.sane()){Serial.println("INVALID OR BUSY");return;}
   cfg=t;save();Serial.printf("SPEED %.2f m/min\n",cfg.speed_m_min);return;
  }
  if(s=="RESET"){
   if(state==RUNNING||state==HOMING){Serial.println("BUSY");return;}
   err="";state=ENABLE_REAL_MOTION?UNHOMED:DISABLED;meters=0;layer=0;turnsInLayer=0;stepCounter=0;
   traverseResidual=0;lowTensionAt=0;disable();Serial.println("RESET");return;
  }
  Serial.println("UNKNOWN COMMAND (STATUS STOP HOME START PAUSE TARGET n SPEED n RESET)");
 }
public:
 void begin(){
  Serial.begin(115200);
  for(int p:{HOME_PIN,FAR_PIN,ESTOP_MONITOR_PIN,GUARD_PIN})pinMode(p,INPUT_PULLUP);
  pinMode(HX_DOUT,INPUT);pinMode(HX_SCK,OUTPUT);digitalWrite(HX_SCK,LOW);
  pinMode(ENC_A,INPUT);pinMode(ENC_B,INPUT);
  for(int p:{STEP_PIN,DIR_PIN,TRAVERSE_STEP,TRAVERSE_DIR,ENABLE_PIN})pinMode(p,OUTPUT);
  disable();active=this;
  if(STANDARD_MACHINE)attachInterrupt(digitalPinToInterrupt(ENC_A),encoderInterrupt,RISING);
  load();if(!cfg.sane())fault("CONFIG");
  Serial.println("OPTICAL FIBER WINDER / ENGINEERING PROTOTYPE / NOT PHYSICALLY VERIFIED");
  if(!ENABLE_REAL_MOTION)Serial.println("SAFETY BUILD LOCK ACTIVE: MOTORS DISABLED");
  lastUpdate=micros();
 }
 void tick(){
  static String cmd="";
  while(Serial.available()){
   char ch=Serial.read();
   if(ch=='\n'||ch=='\r'){if(cmd.length())command(cmd);cmd="";}
   else if(cmd.length()<80)cmd+=ch;
  }
  if((state==RUNNING||state==HOMING)&&!safeInputs()){fault("SAFETY_CHAIN_OPEN");return;}
  const uint32_t now=micros();
  if(state==HOMING){
   if(digitalRead(HOME_PIN)==HIGH){state=READY;disable();Serial.println("READY HOMED");return;}
   if(millis()-homingStarted>HOME_TIMEOUT_MS){fault("HOME_TIMEOUT");return;}
   if((uint32_t)(now-lastPulseAt)>=4000){stepPin(TRAVERSE_STEP);lastPulseAt=now;}
   return;
  }
  if(state!=RUNNING)return;
  if(digitalRead(FAR_PIN)==HIGH){fault("TRAVERSE_FAR_LIMIT_OR_DISCONNECT");return;}
  if(STANDARD_MACHINE){
   // Every sample is required: absent HX711 data or encoder verification -> stop.
   // Raw HX711 sign/scale is implementation-specific and must be calibrated.
   static uint32_t lastSense=0;
   if(millis()-lastSense>=100){
    lastSense=millis();int32_t raw=0;
    if(!hxRead(raw)){fault("LOAD_CELL_TIMEOUT");return;}
    float tension=(raw-hxOffset)*cfg.loadcell_newtons_per_count;
    if(!isfinite(tension)||tension>cfg.tension_limit_n){fault("HIGH_TENSION");return;}
    // Proportional reference controller: reduce take-up speed when tension rises.
    // Cannot be tuned without physical dynamic measurements of brake and dancer.
    float err=(cfg.tension_setpoint_n-tension)/cfg.tension_setpoint_n;
    tensionControlMultiplier=fmaxf(0.25f,fminf(1.15f,1.f+0.12f*err));
    if(tension<cfg.min_tension_n){
      if(lowTensionAt==0)lowTensionAt=millis();
      if(millis()-lowTensionAt>=1000){fault("LOW_TENSION_POSSIBLE_BREAK");return;}
    } else lowTensionAt=0;
    // Encoder check intentionally NOT asserted as verified: configured PPR is a prerequisite;
    // physical no-slip correlation must be implemented/calibrated before unlocking motion.
    if(cfg.encoder_ppr==0){fault("ENCODER_UNCALIBRATED");return;}
    // Compare measured encoder turns against commanded turns in at least one full revolution.
    // Discrepancy -> stop; not a precision guarantee or validated safety function.
    uint32_t stepsNow=stepCounter-stepBaseline;
    if(stepsNow>=MICROSTEPS_REV){
      uint32_t encNow=encoderCount-encoderBaseline;
      float expected=(float)stepsNow*cfg.encoder_ppr/MICROSTEPS_REV;
      if(fabsf((float)encNow-expected)>fmaxf(3.f,expected*0.30f)){
        fault("ENCODER_STEP_MISMATCH");return;
      }
      encoderBaseline=encoderCount;stepBaseline=stepCounter;
    }
   }
  }
  float goal=spindleTargetHz()*tensionControlMultiplier;
  float elapsed=(uint32_t)(now-lastUpdate)/1000000.f;
  if(elapsed>=.001f){
   lastUpdate=now;currentHz=fminf(goal,currentHz+600.f*elapsed);
  }
  if(currentHz>0 && (uint32_t)(now-lastPulseAt)>=(uint32_t)(1000000.f/currentHz)){
   lastPulseAt=now;spoolStep();
  }
 }
};
inline Winder* Winder::active=nullptr;
} // namespace winder
