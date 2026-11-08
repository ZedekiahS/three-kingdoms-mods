"""Write the inspected MTU PNG layout Comment without changing image pixels."""
import struct,zlib
from pathlib import Path
root=Path(__file__).parent/'assets_src_v2'
for p in root.glob('ui/characters/*/composites/large_panel/*/noanim.png'):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
 # Idempotently retain all image chunks and remove only this layout Comment.
 chunks=[];pos=8
 while pos+8<len(b):
  n=struct.unpack_from('>I',b,pos)[0];k=b[pos+4:pos+8];data=b[pos+8:pos+8+n];chunk=b[pos:pos+12+n];pos+=12+n
  if not(k==b'tEXt' and data.startswith(b'Comment\0')):chunks.append(chunk)
  if k==b'IEND':break
 d=('Comment\0[type:'+p.parent.name+';x:-30;y:112;z-order:0;pivot_x:0.5003;pivot_y:0.4997;]').encode()
 t=b'tEXt'+d;chunk=struct.pack('>I',len(d))+t+struct.pack('>I',zlib.crc32(t))
 p.write_bytes(b[:8]+chunks[0]+chunk+b''.join(chunks[1:]))
print('Stamped 81 large-panel PNG layout records.')
