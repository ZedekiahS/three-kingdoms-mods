"""Resolve the two real generic portrait paths against installed pack contents.
Reference: Zades Custom Character Creation, Art/Stills; inspected vanilla assets.
This is a resource lookup regression check, not a substitute for game rendering.
"""
import json,sys,struct,zlib,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT),str(HERE)]
from extract_traits import BASE,index_pack,read_entry
from build import pack
X=json.loads((ROOT/'character_audit/extracted.json').read_text(encoding='utf-8'))
CHARS={r['id']:r for r in json.loads((HERE/'characters.json').read_text(encoding='utf-8'))}
CASES={'lu_su':('water_strategist/male','3k_main_hero_generic_male_water_strategist_face_09'),'han_dang':('fire/male','3k_main_hero_generic_male_fire_face_06')}
OUT=HERE/'route_probe';OUT.mkdir(exist_ok=True)
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))
def transparent(comment=None):
 b=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))
 if comment:b+=chunk(b'tEXt',comment)
 return b+chunk(b'IDAT',zlib.compress(b'\0\0\0\0\0'))+chunk(b'IEND',b'')
def stamp(b,mood,panel):
 # Full-figure coordinates follow the existing inspected full-figure canvas;
 # small-panel placement follows the native generic body panel's centre.
 text=f'Comment\0[type:{mood};x:{-30 if panel=="large_panel" else 0};y:{112 if panel=="large_panel" else 70};z-order:0;pivot_x:0.5000;pivot_y:0.5000;]'.encode()
 pos=8;cs=[]
 while pos+8<=len(b):
  n=struct.unpack_from('>I',b,pos)[0];k=b[pos+4:pos+8];d=b[pos+8:pos+8+n];raw=b[pos:pos+n+12];pos+=n+12
  if not(k==b'tEXt' and d.startswith(b'Comment\0')):cs.append(raw)
  if k==b'IEND':break
 return b[:8]+cs[0]+chunk(b'tEXt',text)+b''.join(cs[1:])
def expected():
 result=[]
 for ident,(native,card) in CASES.items():
  c=CHARS[ident];prefix='ui/characters/'+c['portrait']+'/'
  equipment=set()
  for a in X['assets']:
   src='ui/characters/'+native+'/'
   if a['path'].startswith(src):
    rel=a['path'][len(src):]
    if '/faces/' not in rel and rel.startswith(('composites/','stills/')) and rel.endswith('.png'):equipment.add(rel)
  facepaths=[f'composites/faces/{c["portrait"]}/{panel}/{mood}/face.png' for panel in ['large_panel','small_panel'] for mood in ['norm','angry','happy']]
  stills=[f'stills/{kind}/faces/{large}{c["portrait"]}.png' for kind in ['bobbleheads','halfbody_large','halfbody_small','mini','unitcards'] for large in ['','large/']]
  result.append(dict(id=ident,name=c['name'],native_portrait=native,native_face=card,prefix=prefix,equipment=sorted(equipment),facepaths=facepaths,stills=stills))
 return result
def check(packpath):
 ix={e['path']:e for e in index_pack(packpath)};missing=[];report=[]
 for c in expected():
  wanted=c['facepaths']+c['stills']+c['equipment'];absent=[c['prefix']+p for p in wanted if c['prefix']+p not in ix];missing.extend(absent)
  report.append({'name':c['name'],'expected_paths':len(wanted),'missing':len(absent)})
 print(json.dumps({'lookup':'FAIL' if missing else 'PASS','cases':report,'examples':missing[:4]},ensure_ascii=False))
 return not missing
def main():
 if '--check-old' in sys.argv:raise SystemExit(0 if check(BASE/'syc_portraits_assets.pack') else 1)
 files={};evidence=expected()
 for c in evidence:
  source=HERE/'assets_src_v2'/c['prefix']
  for rel in c['equipment']:
   comment=None
   if rel.startswith('composites/'):
    mood=rel.split('/')[-2];comment=f'Comment\0[type:{mood};x:0;y:0;z-order:0;pivot_x:0.5000;pivot_y:0.5000;]'.encode()
   files[c['prefix']+rel]=transparent(comment)
  for rel in c['facepaths']:
   parts=rel.split('/');panel,mood=parts[-3:-1]
   files[c['prefix']+rel]=stamp((source/f'composites/{panel}/{mood}/noanim.png').read_bytes(),mood,panel)
   # Empty fallback and direct fullbody layers; all actual art lives in faces.
   files[c['prefix']+f'composites/EMPTY/{panel}/{mood}/{mood}.png']=transparent()
   files[c['prefix']+f'composites/{panel}/{mood}/noanim.png']=transparent()
  for rel in c['stills']:
   files[c['prefix']+rel]=(source/rel.replace('/faces/','/')).read_bytes()
  for kind in ['bobbleheads','halfbody_large','halfbody_small','mini','unitcards']:
   for large in ['','large/']:
    files[c['prefix']+f'stills/{kind}/{large}EMPTY.png']=transparent()
    files[c['prefix']+f'stills/{kind}/{large}{CHARS[c["id"]]["portrait"]}.png']=transparent()
 target=OUT/'syc_portraits_route_probe.pack';summary=pack(target,files)
 assert check(target)
 # Assert every outfit layer in each native class has a transparent substitute.
 ix={e['path']:e for e in index_pack(target)}
 for c in evidence:
  for rel in c['equipment']:
   b=read_entry(target,ix[c['prefix']+rel]);assert struct.unpack('>II',b[16:24])==(1,1)
   assert b==files[c['prefix']+rel]
 (OUT/'route_evidence.json').write_text(json.dumps({'reference':'https://steamcommunity.com/sharedfiles/filedetails/?id=1798650568','cases':evidence,'pack':summary,'runtime_passed':False},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
