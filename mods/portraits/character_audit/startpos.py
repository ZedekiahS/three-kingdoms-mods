import hashlib,json,lzma,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from extract_traits import index_pack,read_entry
OUT=Path(__file__).parent
def scan(path):
    return json.loads(subprocess.check_output(['node',str(OUT/'scan_startpos.mjs'),str(path)],encoding='utf-8'))
def main():
    x=json.loads((OUT/'extracted.json').read_text(encoding='utf-8'));results=[]
    temp=OUT/'startpos_current.esf';decoded=OUT/'startpos_decoded.esf'
    for pack in x['packs']:
        p=Path(pack['file'])
        if not (p.name.startswith(('data','fast')) or pack['scope']=='mtu'):continue
        for e in index_pack(p):
            if not e['path'].endswith('.esf') or 'startpos' not in e['path']:continue
            data=read_entry(p,e);temp.write_bytes(data)
            result=scan(temp);c=result['compression']
            if c:
                props=data[c['props']['offset']:c['props']['offset']+c['props']['length']]
                payload=data[c['payload']['offset']:c['payload']['offset']+c['payload']['length']]
                # CA stores a bounded LZMA stream without an EOS marker; its length is in COMPRESSED_DATA_INFO.
                decoder=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
                inner=decoder.decompress(props+struct.pack('<Q',c['size'])+payload)
                assert len(inner)==c['size']
                assert decoder.eof and not decoder.unused_data
                decoded.write_bytes(inner);result=scan(decoded)
                assert not result['compression']
            record=dict(scope=pack['scope'],pack=str(p),path=e['path'],sha256=hashlib.sha256(data).hexdigest(),templates=result['templates'])
            results.append(record)
            print(pack['scope'],e['path'],len(result['templates']),flush=True)
    (OUT/'startpos_references.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    for p in [temp,decoded]:
        assert p.resolve().parent==OUT.resolve()
        if p.exists():p.unlink()
if __name__=='__main__':main()
