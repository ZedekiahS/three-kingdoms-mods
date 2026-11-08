"""Check the actual MTU noanim asset layout and PNG Comment contract.
Guards the specific missing metadata / duplicate face-layer export defects.
Runtime rendering is checked separately using runtime_check.py.
"""
import struct,json,sys
from pathlib import Path
p=Path(__file__).parent;chars=json.loads((p/'characters.json').read_text(encoding='utf-8'));errors=[]
for c in chars:
 root=p/'assets_src_v2/ui/characters'/c['portrait']
 if '--old' in sys.argv:root=p/'assets_src/ui/characters'/c['portrait']
 for mood in ['norm','happy','angry']:
  directory=root/'composites/large_panel'/mood;files=list(directory.glob('*.png'))
  if [f.name for f in files]!=['noanim.png']:errors.append(c['id']+': duplicate or missing fullbody layers')
  file=directory/'noanim.png'
  if not file.exists():continue
  b=file.read_bytes();pos=8;comments=[]
  while pos+8<len(b):
   n=struct.unpack_from('>I',b,pos)[0];k=b[pos+4:pos+8];data=b[pos+8:pos+8+n];pos+=12+n
   if k==b'tEXt':comments.append(data)
   if k==b'IEND':break
  wanted=('Comment\0[type:'+mood+';x:-30;y:112;z-order:0;pivot_x:0.5003;pivot_y:0.4997;]').encode()
  if wanted not in comments:errors.append(c['id']+': missing '+mood+' placement metadata')
 if (root/'composites/faces').exists():errors.append(c['id']+': incompatible fullbody-as-face layers')
if errors:print('FAIL',len(errors),'contract violations; examples:',errors[:5]);raise SystemExit(1)
print('PASS: historical intermediate noanim export only; NOT a runtime or generic-renderer acceptance check.')
