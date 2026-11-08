"""Human-in-the-loop check: the user owns the game; retain screenshot evidence.
Run after selecting Han Dang on the campaign Characters page. PASS requires
one complete standing figure and one correct face per card, without old overlays.
This records the user's observed verdict, not an automated game-render test.
"""
import argparse,json,shutil,hashlib,datetime
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--screenshot',required=True);p.add_argument('--result',choices=['pass','fail'],required=True);p.add_argument('--note',required=True);p.add_argument('--release',default='release_v0.2');a=p.parse_args()
root=Path(__file__).parent;source=Path(a.screenshot);assert source.is_file()
out=root/'runtime_evidence';out.mkdir(exist_ok=True)
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');dest=out/(stamp+'_'+a.result+'.png');shutil.copy2(source,dest)
record={'case':'campaign_character_browser_han_dang','result':a.result,'human_observed':True,'screenshot':dest.name,'note':a.note,'packs':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (root/a.release).glob('*.pack')}}
(out/(stamp+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(a.result.upper()+': '+a.note);raise SystemExit(1 if a.result=='fail' else 0)
