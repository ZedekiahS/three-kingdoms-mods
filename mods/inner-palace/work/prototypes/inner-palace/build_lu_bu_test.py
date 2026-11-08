"""194 romance test: native court UI plus independent posts in Lu Bu's startpos.

Does not touch installed game data or saves. ESF payload roundtrip is mandatory.
"""
import json,lzma,struct,subprocess,sys,hashlib,tempfile,zlib
from pathlib import Path
from native_db import ROOT,read
sys.path.insert(0,str(ROOT))
from extract_traits import BASE,index_pack,read_entry
B=Path(__file__).resolve().parent
D=B/'debug_v1'
D.mkdir(parents=True,exist_ok=True)
ALL_HAN='--all-han' in sys.argv
FIXED='--fixed-slots' in sys.argv
MODE='fixed_fourteen' if FIXED else 'independent_five'
UI_FLAG='--fixed-slots' if FIXED else '--independent-five'
entry_path='campaigns/3k_dlc05_start_pos/startpos_romance.esf'
entries=[]
for pack_name in ['data.pack','fast.pack']:
    for entry in index_pack(BASE/pack_name):
        if entry['path'].startswith('campaigns/') and entry['path'].endswith('.esf') and 'startpos_' in entry['path']:
            if ALL_HAN or entry['path']==entry_path:entries.append((BASE/pack_name,entry))
assert len({e['path'] for _,e in entries})==len(entries)
assert len(entries)==(10 if ALL_HAN else 1)
allowed=D/'han_factions.json'
allowed.write_text(json.dumps([r['key'] for r in read('factions_tables')[2] if r['subculture']=='3k_main_chinese']),encoding='utf8')
def scan(path):
    return json.loads(subprocess.check_output(['node',str(ROOT/'character_audit/scan_startpos.mjs'),str(path)],encoding='utf-8'))
def decompress(data,info):
    c=info['compression'];p=c['props'];s=c['payload']
    return lzma.decompress(data[p['offset']:p['offset']+p['length']]+struct.pack('<Q',c['size'])+data[s['offset']:s['offset']+s['length']],format=lzma.FORMAT_ALONE)
subprocess.run([sys.executable,str(B/'build_court_copy.py'),UI_FLAG],check=True)
# Native ESF uses known-size LZMA without an end marker. The installed 7-Zip
# produces that stream; a single-file archive with uncompressed headers keeps
# its only packed stream between the 32-byte signature and the next header.
# Format reference: ip7z/7zip DOC/7zFormat.txt, DOC/lzma.txt.
from mod_paths import SEVENZIP as sevenzip
assert sevenzip.is_file(), 'Installed 7-Zip is required for native LZMA encoding'
campaigns=[]
for source_pack,entry in entries:
    entry_path=entry['path']
    stem=entry_path.replace('/','_').removesuffix('.esf')
    original=read_entry(source_pack,entry)
    raw=D/(stem+'.original.esf');raw.write_bytes(original)
    decoded=D/(stem+'.decoded.esf');decoded.write_bytes(decompress(original,scan(raw)))
    patched=D/(stem+'.patched.esf')
    command=['node',str(B/'patch_native_posts.mjs'),'posts',str(decoded),str(patched),str(B/(MODE+'_manifest.json'))]
    if ALL_HAN:command.append(str(allowed))
    details=json.loads(subprocess.check_output(command,encoding='utf8'))
    with tempfile.TemporaryDirectory(prefix='post-stream-',dir=D) as scratch:
        archive=Path(scratch)/'stream.7z'
        subprocess.run([str(sevenzip),'a','-t7z',str(archive),str(patched),'-m0=LZMA:d=8m:lc=3:lp=0:pb=2','-mhc=off','-ms=off','-y'],check=True,stdout=subprocess.DEVNULL)
        encoded=archive.read_bytes()
    assert encoded[:6]==b'7z\xbc\xaf\x27\x1c'
    assert zlib.crc32(encoded[12:32])==struct.unpack_from('<I',encoded,8)[0]
    offset,length,crc=struct.unpack_from('<QQI',encoded,12)
    header=encoded[32+offset:]
    assert len(header)==length and zlib.crc32(header)==crc and header[0]==1
    props=bytes.fromhex('5d00008000')
    assert b'\x23\x03\x01\x01\x05'+props in header
    stream=props+struct.pack('<Q',patched.stat().st_size)+encoded[32:32+offset]
    assert lzma.decompress(stream,format=lzma.FORMAT_ALONE)==patched.read_bytes()
    compressed=D/(stem+'.patched.lzma');compressed.write_bytes(stream)
    out=B/(MODE+'_src')/entry_path;out.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['node',str(B/'patch_native_posts.mjs'),'wrap',str(raw),str(out),str(compressed),str(patched.stat().st_size)],check=True,stdout=subprocess.DEVNULL)
    assert decompress(out.read_bytes(),scan(out))==patched.read_bytes()
    campaigns.append(dict(path=entry_path,source_pack=source_pack.name,source_sha256=hashlib.sha256(original).hexdigest(),patched_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),**details))
    print('PASS',entry_path,'factions',len(details['factions']),'posts added',details['added'],flush=True)
source=B/(MODE+'_src')
selected_paths={e['path'] for _,e in entries}
files=sorted(p for p in source.rglob('*') if p.is_file() and (p.suffix!='.esf' or p.relative_to(source).as_posix() in selected_paths))
index=b'';body=b''
for p in files:
    data=p.read_bytes();index+=struct.pack('<IB',len(data),0)+str(p.relative_to(source)).replace('/','\\').encode()+b'\0';body+=data
pack=B/('zz_syc_harem_'+MODE+'.pack');pack.write_bytes(struct.pack('<4s6I',b'PFH5',4,0,0,len(files),len(index),0)+index+body)
manifest=json.loads((B/(MODE+'_manifest.json')).read_text(encoding='utf-8'))
manifest.update(files=[str(p.relative_to(source)) for p in files],campaigns=campaigns,scope='all vanilla Han factions' if ALL_HAN else '194 romance Lu Bu only',limits='New campaign required; existing saves are not migrated. Competing startpos mods require compatibility work. New marriages are not created; existing leader spouse can fill an empty queen office.')
(B/(MODE+'_manifest.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
subprocess.run([sys.executable,str(B/'verify_court_copy.py'),UI_FLAG],check=True)
print('PASS: original ESF untouched; complete compressed payload roundtrip; native data preserved; campaigns',len(campaigns),'bytes',pack.stat().st_size)
