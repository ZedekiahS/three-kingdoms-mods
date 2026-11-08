"""Read/write the local game's DB formats using its RPFM schema; assert round trips."""
import re, struct, sys, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from extract_traits import BASE,index_pack,read_entry
SCHEMA=(ROOT/'schema_3k.ron').read_text(encoding='utf-8')
def fields(table,version):
    section=SCHEMA.split('        "'+table+'": [',1)[1].split('\n        "',1)[0]
    block=re.split(r'\n                version: ',section)[1:]
    block=next(b for b in block if b.startswith(str(version)+','))
    return re.findall(r'name: "([^"]+)",\s+field_type: (\w+)',block.split('localised_fields:')[0])
def read(table):
    e=next(e for e in index_pack(BASE/'database.pack') if e['path']=='db/'+table+'/data__')
    data=read_entry(BASE/'database.pack',e);p=4
    n=struct.unpack_from('<H',data,p)[0];p+=2+n*2
    version=0
    if data[p:p+4]==b'\xfc\xfd\xfe\xff':version=struct.unpack_from('<I',data,p+4)[0];p+=8
    p+=1;count=struct.unpack_from('<I',data,p)[0];p+=4
    header=data[:p-4];schema=fields(table,version)
    def value(t):
        nonlocal p
        if t.startswith('Optional'):
            yes=data[p];p+=1
            return value(t[8:]) if yes else None
        if t=='StringU8':
            n=struct.unpack_from('<H',data,p)[0];p+=2;v=data[p:p+n].decode();p+=n;return v
        fmt={'I32':'i','I64':'q','F32':'f','Boolean':'?'}[t]
        v=struct.unpack_from('<'+fmt,data,p)[0];p+=struct.calcsize(fmt);return v
    rows=[{k:value(t) for k,t in schema} for _ in range(count)]
    assert p==len(data),(table,p,len(data))
    assert write(header,schema,rows)==data,table
    return header,schema,rows
def write(header,schema,rows):
    def value(t,v):
        if t.startswith('Optional'):return b'\0' if v is None else b'\1'+value(t[8:],v)
        if t=='StringU8':
            b=v.encode();return struct.pack('<H',len(b))+b
        return struct.pack('<'+{'I32':'i','I64':'q','F32':'f','Boolean':'?'}[t],v)
    return header+struct.pack('<I',len(rows))+b''.join(value(t,r[k]) for r in rows for k,t in schema)

def independent_header(header, identity):
    """New table instance, retaining the verified vanilla schema/header flags."""
    assert header[:4]==b'\xfd\xfe\xfc\xff'
    old_chars=struct.unpack_from('<H',header,4)[0]
    guid=str(uuid.uuid5(uuid.NAMESPACE_URL,'syc-inner-palace-db/'+identity))
    encoded=guid.encode('utf-16-le')
    return header[:4]+struct.pack('<H',len(guid))+encoded+header[6+old_chars*2:]
if __name__=='__main__':
    import json
    for t in ['ministerial_positions_tables','ministerial_positions_culture_details_tables','ministerial_positions_to_government_types_tables','ministerial_positions_to_character_effects_tables','ministerial_positions_to_effects_tables']:
        h,s,rows=read(t)
        print(t,len(rows),s)
        print(json.dumps([r for r in rows if any('minister_earth' in str(v) or 'prime_minister' in str(v) for v in r.values())][:4],ensure_ascii=False,indent=2))
