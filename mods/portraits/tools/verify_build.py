"""Static regression only: pack integrity, binding isolation and known bad paths."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'work/prototypes/portrait-pack'
sys.path[:0]=[str(ROOT),str(P),str(ROOT/'character_audit')]
from extract_traits import index_pack,read_entry
from extract import decode
from build import load_tables,TABLES
import generic_route_probe as route
chars=json.loads((P/'characters.json').read_text(encoding='utf8'));targets={c['template']:c for c in chars}
for profile,name in [('base','syc_portraits_vanilla.pack'),('mtu','syc_portraits_mtu33.pack')]:
 path=ROOT/'dist'/name;ix=index_pack(path)
 assert len(ix)==11, 'Expected 3 DB tables and 8 startpos files'
 assert not any(e['path'].endswith(('.ccd','.lua','.loc')) for e in ix)
 baseline={r['key']:r for r in load_tables(profile)[TABLES[2]]}
 entry=next(e for e in ix if e['path'].startswith('db/'+TABLES[2]+'/'))
 rows=decode(TABLES[2],read_entry(path,entry))['rows'];assert len(rows)==27
 for row in rows:
  assert row['art_set_override']==targets[row['key']]['art_set']
  assert {k for k in row if row[k]!=baseline[row['key']][k]}=={'art_set_override'}
route.CASES.update(lu_meng=('metal/male','3k_main_hero_generic_male_metal_face_06'))
assert not route.check(ROOT/'dist/syc_portraits_assets.pack'), 'Known-bad base must fail generic-path check'
assert route.check(ROOT/'dist/syc_portraits_route_probe.pack')
receipt=json.loads((ROOT/'dist/build_receipt.json').read_text(encoding='utf8'))
for name,sha in receipt['files'].items():assert hashlib.sha256((ROOT/'dist'/name).read_bytes()).hexdigest()==sha
print('PASS: isolated bindings, pack readback and three-character generic-path regression. Game runtime NOT tested by this command.')
