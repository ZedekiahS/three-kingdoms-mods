import struct

def parse_loc(data):
    assert data[2:5] == b'LOC'
    count = struct.unpack_from('<I', data, 10)[0]
    pos = 14
    rows = []
    for _ in range(count):
        fields = []
        for _ in range(2):
            size = struct.unpack_from('<H', data, pos)[0] * 2
            pos += 2
            fields.append(data[pos:pos + size].decode('utf-16-le'))
            pos += size
        fields.append(bool(data[pos]))
        pos += 1
        rows.append(fields)
    assert pos == len(data), (pos, len(data))
    return rows
