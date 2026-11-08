"""Read-only audit of installed 3K packs; reuse workspace PFH5 and RPFM schema readers."""
import collections, hashlib, json, re, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'work/prototypes/inner-palace'))
from extract_traits import BASE, index_pack, read_entry
from read_mods import parse_loc
from native_db import fields, SCHEMA

OUT = Path(__file__).parent
from mod_paths import WORKSHOP as MOD
TABLES = {
    'character_generation_templates_tables',
    'character_generation_template_game_mode_details_tables',
    'campaign_character_art_sets_tables', 'campaign_character_arts_tables',
    'ceos_to_equipment_variants_tables', 'names_tables',
    'campaign_character_art_set_campaign_junctions_tables',
    'ceo_initial_datas_tables',
}

def decode(table, data):
    p = 0
    if data[:4] == b'\xfd\xfe\xfc\xff':
        p = 4
        n = struct.unpack_from('<H', data, p)[0]
        p += 2 + n * 2
    version = 0
    if data[p:p+4] == b'\xfc\xfd\xfe\xff':
        version = struct.unpack_from('<I', data, p+4)[0]
        p += 8
    assert data[p] == 1, (table, data[:30].hex(), p)
    p += 1
    count = struct.unpack_from('<I', data, p)[0]
    p += 4
    schema = fields(table, version)
    section = SCHEMA.split('        "'+table+'": [',1)[1].split('\n        "',1)[0]
    block = next(b for b in re.split(r'\n                version: ', section)[1:] if b.startswith(str(version)+','))
    key_fields = re.findall(r'name: "([^"]+)",\s+field_type: \w+,\s+is_key: true', block.split('localised_fields:')[0])
    header = data[:p]
    fmts = {'I32':'i', 'I64':'q', 'F32':'f', 'F64':'d', 'Boolean':'?','I16':'h'}
    def value(t):
        nonlocal p
        if t.startswith('Optional'):
            yes = data[p]; p += 1
            assert yes in (0,1)
            return value(t[8:]) if yes else None
        if t in ('StringU8','StringU16'):
            n = struct.unpack_from('<H', data, p)[0]; p += 2
            size = n * (2 if t == 'StringU16' else 1)
            v = data[p:p+size].decode('utf-16-le' if t == 'StringU16' else 'utf-8'); p += size
            return v
        fmt = fmts[t]
        v = struct.unpack_from('<'+fmt, data, p)[0]; p += struct.calcsize(fmt)
        return v
    rows = [{k:value(t) for k,t in schema} for _ in range(count)]
    assert p == len(data), (table, p, len(data))
    def encode(t,v):
        if t.startswith('Optional'):
            return b'\0' if v is None else b'\1'+encode(t[8:],v)
        if t in ('StringU8','StringU16'):
            b = v.encode('utf-16-le' if t=='StringU16' else 'utf-8')
            return struct.pack('<H',len(b)//(2 if t=='StringU16' else 1))+b
        return struct.pack('<'+fmts[t],v)
    assert header+b''.join(encode(t,r[k]) for r in rows for k,t in schema) == data, table
    return dict(version=version,fields=schema,keys=key_fields,rows=rows)
