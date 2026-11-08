"""Add Lu Meng's verified generic route; retain both prior characters byte for byte."""
import json,subprocess
from pathlib import Path
import generic_route_probe as route
from build import pack
from extract_traits import index_pack,read_entry

HERE=Path(__file__).resolve().parent
OUT=HERE/'route_probe_v3';OUT.mkdir(exist_ok=True)
route.CASES={'lu_meng':('metal/male','3k_main_hero_generic_male_metal_face_06')}
route.OUT=OUT
route.main()
target=OUT/'syc_portraits_route_probe.pack'
added={e['path']:read_entry(target,e) for e in index_pack(target)}
subprocess.run(['node',str(HERE/'fix_bobbleheads.cjs'),'--lu-meng'],check=True)
for f in (OUT/'assets').rglob('*.png'):
 added[f.relative_to(OUT/'assets').as_posix()]=f.read_bytes()
assert all(k.startswith('ui/characters/syc_portrait_lu_meng/') for k in added)
previous=HERE/'route_probe_v2/syc_portraits_route_probe.pack'
old={e['path']:read_entry(previous,e) for e in index_pack(previous)}
assert not set(old)&set(added)
files=old|added
summary=pack(target,files)
assert route.check(target)
ix={e['path']:e for e in index_pack(target)}
assert all(read_entry(target,ix[k])==v for k,v in old.items())
summary.update(added_character='lu_meng',added_entries=len(added),unchanged_previous_entries=len(old),runtime_passed=False)
(OUT/'build_receipt.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary))
