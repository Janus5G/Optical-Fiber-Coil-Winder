#!/usr/bin/env python3
"""Verify SHA256SUMS.txt in release root; no external API or dependencies."""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parents[1]
manifest=root/'SHA256SUMS.txt'
if not manifest.exists():raise SystemExit('FAIL: missing SHA256SUMS.txt')
count=0;failed=[]
for ln in manifest.read_text().splitlines():
 if not ln.strip():continue
 try: digest,relative=ln.split('  ',1)
 except ValueError:failed.append('malformed line: '+ln);continue
 target=root/relative
 if not target.exists():failed.append('missing: '+relative);continue
 calc=hashlib.sha256(target.read_bytes()).hexdigest()
 if calc!=digest:failed.append('digest mismatch: '+relative)
 count+=1
# Detect unexpected source payloads missing from signed inventory
ignore={'SHA256SUMS.txt'}
allpaths={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and
          '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.name not in ignore}
signed={x.split('  ',1)[1] for x in manifest.read_text().splitlines() if '  ' in x}
for missed in sorted(allpaths-signed):failed.append('unlisted file: '+missed)
if failed:
 for e in failed:print('FAIL',e)
 raise SystemExit(1)
print('PASS: SHA-256 verified',count,'listed release files')
