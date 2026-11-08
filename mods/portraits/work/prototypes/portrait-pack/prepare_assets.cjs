// Deterministic game texture export; source illustrations are never overwritten.
const fs=require('node:fs'),path=require('node:path'),sharp=require('sharp');
const root=path.resolve(__dirname,'../../..'),out=path.join(__dirname,'assets_src_v2');
const jobs=JSON.parse(fs.readFileSync(path.join(__dirname,'characters.json'),'utf8'));
async function save(buf,rel){const p=path.join(out,rel);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,buf);}
async function fit(input,w,h){return sharp(input).resize(w,h,{fit:'contain',background:'#00000000'}).png().toBuffer();}
async function main(){const manifest=[];
 for(const c of jobs){const input=path.join(root,c.source),meta=await sharp(input).metadata(),prefix=`ui/characters/${c.portrait}`;
  const largeFigure=await fit(input,820,1120),large=await sharp({create:{width:1300,height:1300,channels:4,background:'#00000000'}}).composite([{input:largeFigure,left:260,top:100}]).png().toBuffer();
  const small=await fit(input,645,900);
  for(const [panel,buf] of [['large_panel',large],['small_panel',small]])for(const mood of ['norm','happy','angry']){
   await save(buf,`${prefix}/composites/${panel}/${mood}/noanim.png`);
  }
  const cx=Math.round(meta.width*c.face_x),cy=Math.round(meta.height*c.face_y);
  const headBox={left:Math.max(0,cx-155),top:Math.max(0,cy-170),width:310,height:380};
  const head=await sharp(input).extract(headBox).png().toBuffer();
  const upper=await sharp(input).extract({left:Math.max(0,Math.min(meta.width-700,cx-350)),top:Math.max(0,cy-150),width:700,height:650}).png().toBuffer();
  const strip=await sharp(input).extract({left:Math.max(0,Math.min(meta.width-360,cx-180)),top:Math.max(0,cy-200),width:360,height:970}).resize(131,353).png().toBuffer();
  const unitcard=await sharp({create:{width:131,height:435,channels:4,background:'#00000000'}}).composite([{input:strip,left:0,top:82}]).png().toBuffer();
  for(const [kind,w,h,source] of [['bobbleheads',84,138,head],['halfbody_large',312,250,upper],['halfbody_small',110,84,upper],['mini',30,30,head],['unitcards',82,272,unitcard]])for(const high of [false,true]){
   const ww=high?Math.round(w*1.6):w,hh=high?Math.round(h*1.6):h,buf=await fit(source,ww,hh),dir=high?'large/':'';
   await save(buf,`${prefix}/stills/${kind}/${dir}${c.portrait}.png`);
  }
  manifest.push({name:c.name,portrait:c.portrait,source:c.source,sourceSize:[meta.width,meta.height],headBox});
 }
 fs.writeFileSync(path.join(__dirname,'asset_manifest.json'),JSON.stringify(manifest,null,2));console.log('Exported',jobs.length,'portraits');
}
main().catch(e=>{console.error(e);process.exit(1)});
