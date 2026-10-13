from pathlib import Path
import json,csv,hashlib,re,urllib.parse
ROOT=Path(__file__).resolve().parents[1]

def test_es32_firmware_physical_build_lock():
 for machine in ('budget-v1','standard-v1'):
  text=(ROOT/machine/'firmware/src/main.cpp').read_text()
  assert '#define ENABLE_REAL_MOTION 0' in text

def test_docs_links_resolve():
 # local relative markdown links; heading-only fragments ignored
 for p in ROOT.rglob('*.md'):
  if any(v in p.parts for v in ('.git','.venv')):continue
  body=p.read_text(encoding='utf-8')
  for path in re.findall(r'(?<!!)\[[^]]+\]\(([^)]+)\)',body):
   value=urllib.parse.unquote(path).split('#',1)[0]
   if not value or value.startswith(('http:','https:','mailto:','data:')):continue
   assert (p.parent/value).exists(),f'broken link in {p}: {value}'

def test_bom_totals_reproducible():
 summary=json.loads((ROOT/'results'/'bom_summary.json').read_text())
 for machine,info in summary.items():
  with (ROOT/machine/'bom'/'bom.csv').open() as f:rows=list(csv.DictReader(f))
  total=sum(int(row['extended_estimate_dkk']) for row in rows)
  assert total==info['budget_estimate_dkk']
  assert all(row['status']=='ESTIMATE' and row['supplier_reference']=='NOT VERIFIED' for row in rows)

def test_capacity_scenarios_are_transparent():
 rows=json.loads((ROOT/'results'/'capacity_scenarios.json').read_text())
 assert len(rows)==36
 assert all(row['physically_qualified'] is False for row in rows)

def test_firmware_platformio_files_exist():
 for machine in ('budget-v1','standard-v1'):
  assert (ROOT/machine/'firmware/platformio.ini').exists()
  assert (ROOT/machine/'electronics/concept_wiring.svg').exists()

def test_no_external_repo_code_reference_dependency():
 # repo must not contain external Caffeine/PRISME/Q8 runtime imports
 for p in (ROOT/'common').rglob('*.py'):
  text=p.read_text()
  assert 'import caffeine' not in text.lower()

def test_nc_switch_firmware_polarity_matches_concept_wiring():
 s=(ROOT/'common/controller/embedded/winder.hpp').read_text()
 assert 'digitalRead(HOME_PIN)==HIGH' in s
 assert 'digitalRead(FAR_PIN)==HIGH' in s
 assert 'digitalRead(ESTOP_MONITOR_PIN)==LOW' in s

def test_hardwired_estop_not_confused_with_software_enable():
 s=(ROOT/'docs/SAFETY.md').read_text()
 assert 'independent' in s.lower()
 assert 'GPIO25' in s
 assert 'motor-energy isolation' in s


def test_original_concept_illustrations_match_source_manifest():
 """Source integrity only: image bytes match recorded incoming attachment hashes."""
 manifest=json.loads((ROOT/'assets/original-concept-images/SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
 assert manifest['schema_version']==1
 assert {item['file'] for item in manifest['images']}=={'budget-original.png','standard-original.png'}
 for item in manifest['images']:
  f=ROOT/'assets/original-concept-images'/item['file']
  raw=f.read_bytes()
  assert raw[:8]==b'\x89PNG\r\n\x1a\n'
  assert hashlib.sha256(raw).hexdigest()==item['sha256']
  assert len(raw)==item['size_bytes']
  assert list(__import__('struct').unpack('>II',raw[16:24]))==item['dimensions_px']
