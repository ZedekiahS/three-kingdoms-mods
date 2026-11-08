import json, struct, re, collections
from pathlib import Path
from read_mods import parse_loc
from mod_paths import GAME_DATA as BASE
OUT=Path('trait_readout'); OUT.mkdir(exist_ok=True)

def index_pack(path):
    with path.open('rb') as f:
        magic,flags,dc,ds,n,sz,ts=struct.unpack('<4s6I',f.read(28))
        assert magic==b'PFH5' and not flags & (128|256), (magic,flags)
        f.read(ds); ix=f.read(sz); pos=0; off=f.tell(); rows=[]
        for _ in range(n):
            size=struct.unpack_from('<I',ix,pos)[0]; pos+=4
            if flags&64: pos+=4
            comp=ix[pos];pos+=1
            end=ix.index(b'\0',pos); name=ix[pos:end].decode().replace('\\','/');pos=end+1
            rows.append(dict(path=name,size=size,offset=off,compressed=comp));off+=size
        assert pos==sz and off<=path.stat().st_size
        return rows

def read_entry(path,e):
    assert not e['compressed']
    with path.open('rb') as f:
        f.seek(e['offset']); return f.read(e['size'])

if __name__=='__main__':
    for name in ['database.pack','data.pack','local_cn.pack']:
        path=BASE/name; ix=index_pack(path)
        (OUT/(name+'.index.json')).write_text(json.dumps(ix,ensure_ascii=False),encoding='utf-8')
        matches=[e for e in ix if re.search('ceo|trait|character_trait',e['path'])]
        print(name, len(ix),'matches',len(matches))
        print(json.dumps(matches[:25],ensure_ascii=False))
        if name=='local_cn.pack':
            loc={}
            for e in ix:
                if e['path'].endswith('.loc'):
                    for k,v,_ in parse_loc(read_entry(path,e)):loc[k]=v
            (OUT/'cn.json').write_text(json.dumps(loc,ensure_ascii=False),encoding='utf-8')
            hits={k:v for k,v in loc.items() if 'trait' in k and ('name' in k or 'description' in k)}
            (OUT/'trait_loc.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8')
            print('trait loc sample',json.dumps(list(hits.items())[:20],ensure_ascii=False))
