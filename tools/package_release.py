#!/usr/bin/env python3
"""Create a deterministic owner-preview ZIP, SHA-256 inventory and release checksum.
Run AFTER host tests. No VCS actions, no network operations.
"""
from pathlib import Path
import sys,shutil,hashlib,zipfile,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
VERSION='v1.0.0-RC1.1'
ZIP=OUT/f'Optical-Fiber-Coil-Winder-{VERSION}.zip'
for p in ROOT.rglob('__pycache__'):
 if p.is_dir():shutil.rmtree(p)
for p in ROOT.rglob('.pytest_cache'):
 if p.is_dir():shutil.rmtree(p)
report=json.loads((ROOT/'results'/'test_report.json').read_text())
if report['summary']['FAIL'] or report['summary']['SKIP'] or report['status']!='SOFTWARE_PASS / HARDWARE_HOLD':
 raise SystemExit('Refusing release packaging with failed host evidence.')
source_files=sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt'), key=lambda p:p.relative_to(ROOT).as_posix())
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix() for p in source_files]
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
source_files.append(ROOT/'SHA256SUMS.txt')
source_files.sort(key=lambda p:p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as zipf:
 for p in source_files:
  zpath=f'{ROOT.name}/'+p.relative_to(ROOT).as_posix()
  info=zipfile.ZipInfo(zpath,date_time=(2026,10,13,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=(0o644 & 0xFFFF)<<16
  zipf.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
zipsha=hashlib.sha256(ZIP.read_bytes()).hexdigest()
sha_path=OUT/f'Optical-Fiber-Coil-Winder-{VERSION}.zip.sha256'
sha_path.write_text(f'{zipsha}  {ZIP.name}\n')
# Check zip members and file hash from the archive itself; no unresolved placeholders.
with zipfile.ZipFile(ZIP) as z:
 bad=z.testzip()
 if bad:raise SystemExit('Corrupt ZIP member: '+bad)
 for line in lines:
  digest,name=line.split('  ',1)
  actual=hashlib.sha256(z.read(f'{ROOT.name}/{name}')).hexdigest()
  if actual!=digest:raise SystemExit(f'Integrity mismatch in ZIP: {name}')
print(f'Created {ZIP}, {len(source_files)} files, {ZIP.stat().st_size} bytes')
print('SHA256',zipsha)
