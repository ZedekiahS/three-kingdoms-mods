"""Build separate vanilla/MTU portrait profiles from verified local game packs.
No CEO, gameplay script, stats, skills, item or localisation overrides.
"""
import sys,json,struct,hashlib,subprocess,lzma,uuid,copy,tempfile,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
(HERE/'reference').mkdir(exist_ok=True)
sys.path[:0]=[str(ROOT),str(ROOT/'character_audit'),str(ROOT/'work/prototypes/inner-palace')]
from extract_traits import BASE,index_pack,read_entry
from extract import decode
from native_db import read,write,independent_header
from startpos import scan
from mod_paths import WORKSHOP as MOD, SEVENZIP
MTU=MOD/'1812159400/[mod]Lady_bian_FLC.pack'
RELEASE=HERE/'release_v0.2';RELEASE.mkdir(exist_ok=True)

TABLES=['campaign_character_art_sets_tables','campaign_character_arts_tables','character_generation_templates_tables']
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def native_compress(original,patched):
 # Reuse the workspace's game-tested bounded-LZMA wrapper, rather than inventing an ESF container.
 sevenzip=SEVENZIP;assert sevenzip.is_file()
 with tempfile.TemporaryDirectory(prefix='portrait-stream-',dir=HERE/'reference') as scratch:
  archive=Path(scratch)/'stream.7z'
  subprocess.run([str(sevenzip),'a','-t7z',str(archive),str(patched),'-m0=LZMA:d=8m:lc=3:lp=0:pb=2','-mhc=off','-ms=off','-y'],check=True,stdout=subprocess.DEVNULL)
  encoded=archive.read_bytes()
 assert encoded[:6]==b'7z\xbc\xaf\x27\x1c' and zlib.crc32(encoded[12:32])==struct.unpack_from('<I',encoded,8)[0]
 offset,length,crc=struct.unpack_from('<QQI',encoded,12);header=encoded[32+offset:]
 assert len(header)==length and zlib.crc32(header)==crc
 props=bytes.fromhex('5d00008000');assert b'\x23\x03\x01\x01\x05'+props in header
 stream=props+struct.pack('<Q',patched.stat().st_size)+encoded[32:32+offset]
 assert lzma.decompress(stream,format=lzma.FORMAT_ALONE)==patched.read_bytes()
 compressed=HERE/'reference/current.lzma';compressed.write_bytes(stream);wrapped=HERE/'reference/current_wrapped.esf'
 subprocess.run(['node',str(ROOT/'work/prototypes/inner-palace/patch_native_posts.mjs'),'wrap',str(original),str(wrapped),str(compressed),str(patched.stat().st_size)],check=True,stdout=subprocess.DEVNULL)
 d=wrapped.read_bytes();c=scan(wrapped)['compression'];assert lzma.decompress(d[c['props']['offset']:c['props']['offset']+c['props']['length']]+struct.pack('<Q',c['size'])+d[c['payload']['offset']:c['payload']['offset']+c['payload']['length']],format=lzma.FORMAT_ALONE)==patched.read_bytes()
 return d
def pack(path,files):
 ix=bytearray();payload=[]
 for name,data in sorted(files.items()):
  assert not name.startswith('/') and '..' not in name.split('/')
  ix+=struct.pack('<IB',len(data),0)+name.replace('/','\\').encode()+b'\0';payload.append(data)
 path.write_bytes(struct.pack('<4s6I',b'PFH5',3,0,0,len(files),len(ix),0)+ix+b''.join(payload))
 entries=index_pack(path);assert len(entries)==len(files)
 for e in entries:assert read_entry(path,e)==files[e['path']]
 return {'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'entries':len(files),'roundtrip':True}
def load_tables(profile):
 result={};parts={t:[] for t in TABLES}
 for p in [BASE/'database.pack']+([MTU] if profile=='mtu' else []):
  for e in index_pack(p):
   if e['path'].startswith('db/') and e['path'].split('/')[1] in TABLES:
    t=e['path'].split('/')[1];d=decode(t,read_entry(p,e));parts[t].append((e['path'],d))
 for t,files in parts.items():
  rows={}
  for name,d in sorted(files):
   for r in d['rows']:rows.setdefault(tuple(r[k] for k in d['keys']),r)
  result[t]=list(rows.values())
 return result
def build_profile(profile,chars):
 tables=load_tables(profile);templates={r['key']:r for r in tables[TABLES[2]]};sets={r['art_set_id']:r for r in tables[TABLES[0]]}
 outrows={t:[] for t in TABLES};evidence=[];usedids={r['id'] for r in tables[TABLES[1]]}
 for i,c in enumerate(chars):
  t=copy.deepcopy(templates[c['template']]);oldset=t['art_set_override'];t['art_set_override']=c['art_set'];outrows[TABLES[2]].append(t)
  s=copy.deepcopy(sets[oldset]);s['art_set_id']=c['art_set'];s['is_custom']=True;outrows[TABLES[0]].append(s)
  artrows=[copy.deepcopy(r) for r in tables[TABLES[1]] if r['art_set_id']==oldset]
  assert any(r['has_come_of_age'] for r in artrows)
  for j,r in enumerate(artrows):
   new_id=1900000000+i*32+j
   assert new_id not in usedids;usedids.add(new_id);r['id']=new_id;r['art_set_id']=c['art_set']
   if r['has_come_of_age']:r.update(portrait=c['portrait']+'/',card=c['portrait'],fallback_composite_display='EMPTY')
   outrows[TABLES[1]].append(r)
  evidence.append({'name':c['name'],'template':c['template'],'previous_art_set':oldset,'new_art_set':c['art_set'],'original_is_male':t['is_male'],'art_rows':len(artrows),'template_changed_fields':['art_set_override']})
 files={}
 for table,rows in outrows.items():
  header,schema,_=read(table);header=independent_header(header,'portrait-27/'+profile+'/'+table)
  data=write(header,schema,rows);assert decode(table,data)['rows']==rows
  files['db/'+table+'/!syc_portraits_27']=data
 # Keep the actual profile's startpos unchanged except target art-set references.
 refs=json.loads((ROOT/'character_audit/startpos_references.json').read_text(encoding='utf-8'));sources={}
 for r in refs:
  if '8p_start_pos' in r['path']:continue
  if r['scope']=='base' or profile=='mtu' and r['scope']=='mtu':sources[r['path']]=Path(r['pack'])
 mapping={c['template']:c['art_set'] for c in chars};mappingfile=HERE/'binding_map.json';dump(mappingfile,mapping)
 startreports=[];temp=HERE/'reference/current_startpos.esf';raw=HERE/'reference/current_raw.esf';patched=HERE/'reference/current_patched.esf'
 for name,p in sources.items():
  e=next(e for e in index_pack(p) if e['path']==name);data=read_entry(p,e);temp.write_bytes(data);compression=scan(temp)['compression']
  if compression:
   cp=compression;props=data[cp['props']['offset']:cp['props']['offset']+cp['props']['length']];payload=data[cp['payload']['offset']:cp['payload']['offset']+cp['payload']['length']]
   inner=lzma.decompress(props+struct.pack('<Q',cp['size'])+payload,format=lzma.FORMAT_ALONE);assert len(inner)==cp['size']
  else:inner=data
  raw.write_bytes(inner)
  result=json.loads(subprocess.check_output(['node',str(HERE/'patch_startpos.mjs'),str(raw),str(patched),str(mappingfile)],encoding='utf-8'))
  assert scan(patched)['templates']==scan(raw)['templates']
  files[name]=native_compress(temp,patched) if compression else patched.read_bytes()
  result.update(path=name,source=str(p),source_sha256=hashlib.sha256(data).hexdigest());startreports.append(result)
  print(profile,name,len(result['changes']),'art bindings updated',flush=True)
 name='syc_portraits_'+('vanilla' if profile=='base' else 'mtu33')+'.pack'
 packed=pack(RELEASE/name,files)
 dump(HERE/(profile+'_manifest.json'),dict(profile=profile,characters=evidence,startpos=startreports,pack=packed))
 return packed
def main():
 chars=json.loads((HERE/'characters.json').read_text(encoding='utf8'))
 if '--prepare' in sys.argv:return
 if '--reuse-assets' not in sys.argv:subprocess.run(['node',str(HERE/'prepare_assets.cjs')],check=True)
 subprocess.run([sys.executable,str(HERE/'stamp_metadata.py')],check=True)
 subprocess.run([sys.executable,str(HERE/'check_portrait_contract.py')],check=True)
 assets={str(p.relative_to(HERE/'assets_src_v2')).replace('\\','/'):p.read_bytes() for p in (HERE/'assets_src_v2').rglob('*.png')}
 packs=[pack(RELEASE/'syc_portraits_assets.pack',assets)]
 for profile in ['base','mtu']:packs.append(build_profile(profile,chars))
 dump(RELEASE/'build_summary.json',{'characters':27,'profiles':['vanilla','MTU 3.3'],'packs':packs,'runtime_verified':False,'new_campaign_required':True})
 print(json.dumps(packs,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
