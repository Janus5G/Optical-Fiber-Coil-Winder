#!/usr/bin/env python3
"""Central repeatable PASS/FAIL/SKIP/BLOCKED evidence with separate physical test holds."""
import subprocess,sys,platform,xml.etree.ElementTree as ET,json,datetime,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
(R/'results').mkdir(exist_ok=True)
cmd=[sys.executable,'-m','pytest',str(R/'tests'),'-q',f'--junitxml={R / "results" / "junit.xml"}']
run=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
root=ET.parse(R/'results'/'junit.xml').getroot()
cases=[]
for case in root.findall('.//testcase'):
 name=f'{case.attrib.get("classname")}.{case.attrib.get("name")}'
 status='PASS'
 for tag,label in [('failure','FAIL'),('error','FAIL'),('skipped','SKIP')]:
  if case.find(tag) is not None:status=label;break
 cases.append({'name':name,'status':status,'seconds':float(case.attrib.get('time',0))})
blocked=[
 ('PHYSICAL-01','Measured spindle shaft/bearing fit and runout'),
 ('PHYSICAL-02','3D-printed drum strength and flange retention'),
 ('PHYSICAL-03','Spindle/brake/dancer alignment'),
 ('PHYSICAL-04','NC safety circuit and independent energy cutoff/restart prevention'),
 ('PHYSICAL-05','Standard enclosure guarding and interlock validation'),
 ('PHYSICAL-06','Control panel and driver current/thermal/electrical validation'),
 ('PHYSICAL-07','Encoder PPR and length cross-check'),
 ('PHYSICAL-08','Load-cell calibration; dynamic tension response and fiber-break verification'),
 ('PHYSICAL-09','Traverse repeatability, homing and travel limit verification'),
 ('PHYSICAL-10','200-300 m real fiber spool tests'),
 ('PHYSICAL-11','10 km real fiber spool test, only qualified thin coated fiber'),
 ('PHYSICAL-12','Optical loss/OTDR before and after, bend-radius validation'),
 ('RELEASE-13','Supplier-qualified bill of materials'),
 ('RELEASE-14','Electrical schematic ERC and safety engineering sign-off'),
 ('RELEASE-15','Firmware compile with pinned toolchain + real hardware integration'),
]
for bid,label in blocked:cases.append({'name':bid+' — '+label,'status':'BLOCKED','seconds':0.0})
summary={k:sum(c['status']==k for c in cases) for k in ('PASS','FAIL','SKIP','BLOCKED')}
report={'project':'Optical-Fiber-Coil-Winder','release':'v1.0.0-RC1.1',
  'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'environment':{'python':sys.version.split()[0], 'platform':platform.platform()},
  'suite':'host/offline software; no physical measurements','test_command':'python tools/run_tests.py',
  'exit_code':run.returncode,'summary':summary,'results':cases,
  'status':'SOFTWARE_PASS / HARDWARE_HOLD' if run.returncode==0 and summary['FAIL']==0 and summary['SKIP']==0 else 'SOFTWARE_INCOMPLETE_OR_FAIL'}
(R/'results'/'test_report.json').write_text(json.dumps(report,indent=2)+'\n')
line=[f"Optical Fiber Coil Winder — RC1.1 host/software-and-package verification",f"UTC {report['date_utc']}",
 f"Host suite: {'PASS' if report['status']=='SOFTWARE_PASS / HARDWARE_HOLD' else 'INCOMPLETE/FAIL'}; Physical/hardware release: HOLD",
 f"Counts: " + ', '.join(f'{k} {n}' for k,n in summary.items()),
 'NOTE: a PASS here is an isolated host/software check, NEVER a real hardware measurement.','']
line.extend(f"[{c['status']}] {c['name']}" for c in cases)
line.extend(['','=== PYTEST STDOUT ===',run.stdout,'=== PYTEST STDERR ===',run.stderr])
(R/'results'/'PASS_FAIL_LOG.txt').write_text('\n'.join(line)+'\n')
(R/'docs'/'VERIFICATION_REPORT.md').write_text(f'''# RC1.1 verification evidence — generated test inventory

Test date (UTC): {report['date_utc']}

Host software/source-integrity checks: **{summary['PASS']} PASS / {summary['FAIL']} FAIL / {summary['SKIP']} SKIP**. Hardware/other release qualification checks: **{summary['BLOCKED']} BLOCKED**.

This is not an approval to operate or manufacture. Nominal CAD dimensions are checked by geometric tests; manufactured hole tolerances, fit, electrical safety and optical signal integrity are **not verified**.

See [`PASS_FAIL_LOG.txt`](../results/PASS_FAIL_LOG.txt), [`test_report.json`](../results/test_report.json) and [`junit.xml`](../results/junit.xml). The benchmark fixture contains **synthetic host events only**. No physical fiber was wound and no sensor readings were taken.

## Critical holds

- Original owner-supplied concept illustrations are now attached unchanged, with SHA-256 source manifests; publication rights still require owner review.
- No hardware assembly, no independent emergency-stop qualification, no commissioning.
- No verified product-specific minimum bend radius or approved fiber tension settings.
- No measured shaft alignment, thermal behavior, print failure loads or load-cell calibration.
- No real test at 200–300 m or 10 km, and no optical insertion loss/OTDR evidence.
- No KiCad/ERC-ready design, no firmware build against a pinned ESP32 toolchain in this environment.
- Budget estimates are unquoted planning figures, not confirmed supply prices.

**Disposition: Software demonstrator/geometry engineering RC1 only; all prototype manufacturing and public "tested hardware" claims remain HOLD.**
''')
print('\n'.join(line[:6]));sys.exit(0 if report['status']=='SOFTWARE_PASS / HARDWARE_HOLD' else 1)
