"""Rebuild the paused experimental candidate from locally installed CA packs.

Does not install, launch the game, alter saves, or fetch third-party Mod assets.
"""
from pathlib import Path
import argparse, os, sys, subprocess, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--game-data',required=True)
parser.add_argument('--sevenzip',required=True)
args=parser.parse_args()
os.environ['TW3K_DATA']=str(Path(args.game_data).resolve())
os.environ['TW3K_7ZIP']=str(Path(args.sevenzip).resolve())
os.chdir(ROOT)
sys.path.insert(0,str(ROOT))
from extract_traits import index_pack,read_entry,BASE

B=ROOT/'work/prototypes/inner-palace'
out=B/'fixed_fourteen_src'
if out.exists() and any(out.iterdir()):
    raise SystemExit('Use a clean checkout/build directory: existing generated files may contaminate the pack.')
required=['family_court_panel','court_screen_info_lists','court_screen_minister_slot','court_screen','court_screen_imperial_court']
index={e['path']:e for e in index_pack(BASE/'data.pack')}
receipt={'status':'build only; not game acceptance','inputs':{}}
for name in required:
    path='ui/campaign ui/'+name+'.twui.xml'
    data=read_entry(BASE/'data.pack',index[path])
    target=ROOT/'court_readout/vanilla'/path
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    receipt['inputs'][path]=hashlib.sha256(data).hexdigest()
for name in ['database.pack','data.pack','fast.pack']:
    with (BASE/name).open('rb') as f:receipt['inputs'][name]=hashlib.file_digest(f,'sha256').hexdigest()
subprocess.run([sys.executable,str(B/'build_lu_bu_test.py'),'--all-han','--fixed-slots'],check=True)
subprocess.run([sys.executable,str(B/'verify_spouse_roster.py')],check=True)
subprocess.run([sys.executable,str(B/'verify_appointment_guard.py'),str(out/'ui/syc_harem_native/minister_slot.twui.xml')],check=True)
pack=B/'zz_syc_harem_fixed_fourteen.pack'
receipt['output']={'sha256':hashlib.sha256(pack.read_bytes()).hexdigest(),'bytes':pack.stat().st_size}
dest=ROOT/'dist';dest.mkdir(exist_ok=True)
(dest/'build_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print('BUILT EXPERIMENTAL CANDIDATE; NOT INSTALLED:',pack)
