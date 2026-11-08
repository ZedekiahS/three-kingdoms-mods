"""Reproduce the experimental 27-portrait pack plus the THREE-character repair.
Does not install, launch the game, mutate saves, or redistribute native inputs.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--game-data',required=True,type=Path)
p.add_argument('--workshop',required=True,type=Path,help='Steam workshop/content/779340 directory (MTU 1812159400 required)')
p.add_argument('--sevenzip',default='C:/Program Files/7-Zip/7z.exe',type=Path)
a=p.parse_args()
os.environ.update(TW3K_DATA=str(a.game_data.resolve()),TW3K_WORKSHOP=str(a.workshop.resolve()),TW3K_7ZIP=str(a.sevenzip.resolve()))
os.chdir(ROOT)
from extract_traits import index_pack,read_entry
MTU=a.workshop/'1812159400/[mod]Lady_bian_FLC.pack'
for f in [a.game_data/'database.pack',a.game_data/'data.pack',MTU,a.sevenzip]:
 if not f.is_file():raise SystemExit('Required local input missing: '+str(f))
subprocess.run(['node','-e',"require('sharp')"],check=True)
project=ROOT/'work/prototypes/portrait-pack'
packs=sorted([f for f in a.game_data.glob('*.pack') if f.name.startswith(('data','fast'))])+[MTU]
inventory={'assets':[],'packs':[]};refs=[];native=project/'route_probe/native_stills';native.mkdir(parents=True,exist_ok=True)
cards={'3k_main_hero_generic_male_fire_face_06','3k_main_hero_generic_male_water_strategist_face_09','3k_main_hero_generic_male_metal_face_06'}
for f in packs:
 scope='mtu' if f==MTU else 'base';ix=index_pack(f)
 inventory['packs'].append({'file':str(f.resolve()),'scope':scope,'size':f.stat().st_size})
 for e in ix:
  name=e['path']
  if name.startswith('ui/characters/'):
   inventory['assets'].append(dict(scope=scope,pack=f.name,**e))
   if '/stills/bobbleheads/faces/' in name and Path(name).stem in cards:
    (native/('_'.join(name.split('/')[5:]))).write_bytes(read_entry(f,e))
  if name.startswith('campaigns/') and 'startpos' in name and name.endswith('.esf'):
   refs.append({'scope':scope,'pack':str(f.resolve()),'path':name})
audit=ROOT/'character_audit';audit.mkdir(exist_ok=True)
(audit/'extracted.json').write_text(json.dumps(inventory),encoding='utf8')
(audit/'startpos_references.json').write_text(json.dumps(refs),encoding='utf8')
def run(*cmd):subprocess.run(list(cmd),check=True,cwd=ROOT)
run(sys.executable,str(project/'build.py'))
run(sys.executable,str(project/'generic_route_probe.py'))
run('node',str(project/'fix_bobbleheads.cjs'))
sys.path.insert(0,str(project))
from build import pack
previous=project/'route_probe/syc_portraits_route_probe.pack'
files={e['path']:read_entry(previous,e) for e in index_pack(previous)}
art=project/'route_probe_v2/assets'
files.update({f.relative_to(art).as_posix():f.read_bytes() for f in art.rglob('*.png')})
pack(project/'route_probe_v2/syc_portraits_route_probe.pack',files)
run(sys.executable,str(project/'add_lu_meng.py'))
dist=ROOT/'dist';dist.mkdir(exist_ok=True)
outputs=list((project/'release_v0.2').glob('*.pack'))+[project/'route_probe_v3/syc_portraits_route_probe.pack']
for f in outputs:shutil.copy2(f,dist/f.name)
receipt={'status':'experimental; only three repaired characters, not a complete 27-character release','runtime_tested_on_this_build':False,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in dist.glob('*.pack')},'inputs':inventory['packs']}
(dist/'build_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
(dist/'SHA256SUMS.txt').write_text('\n'.join(v+'  '+k for k,v in receipt['files'].items())+'\n',encoding='utf8')
print('Build complete. See dist; installation is manual. Read docs/INSTALL.md before enabling.')
