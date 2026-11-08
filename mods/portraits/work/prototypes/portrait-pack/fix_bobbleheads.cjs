// Follow the native court_screen_info_lists bobbleheads canvas and clipping.
const fs=require('node:fs'),path=require('node:path'),sharp=require('sharp'),assert=require('node:assert/strict');
const base=__dirname,root=path.resolve(base,'../../..');
const chars=JSON.parse(fs.readFileSync(path.join(base,'characters.json')));
const cases=[{id:'han_dang',native:'3k_main_hero_generic_male_fire_face_06',face:[400,80,180,190],eyes:[530,142]},
 {id:'lu_su',native:'3k_main_hero_generic_male_water_strategist_face_09',face:[515,115,150,170],eyes:[585,164]}];
const outputDir=process.argv.includes('--lu-meng')?'route_probe_v3':'route_probe_v2';
if(process.argv.includes('--lu-meng'))cases.splice(0,cases.length,{id:'lu_meng',native:'3k_main_hero_generic_male_metal_face_06',face:[405,95,150,160],eyes:[493,147]});
async function bbox(file){const {data,info}=await sharp(file).ensureAlpha().raw().toBuffer({resolveWithObject:true});let x0=info.width,y0=info.height,x1=-1,y1=-1;for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>32){x0=Math.min(x,x0);y0=Math.min(y,y0);x1=Math.max(x,x1);y1=Math.max(y,y1);}return {x:x0,y:y0,w:x1-x0+1,h:y1-y0+1,W:info.width,H:info.height};}
async function main(){const old=process.argv.includes('--check-old'),rows=[],tiles=[];
 for(const c of cases){const def=chars.find(a=>a.id===c.id),input=path.join(root,def.source),meta=await sharp(input).metadata();
  if(old){const scale=84/310,cy=Math.round(meta.height*def.face_y),eyeY=(138-380*scale)/2+(c.eyes[1]-(cy-170))*scale;rows.push({id:c.id,eyeY,visible:eyeY>=61&&eyeY<=113});continue;}
  for(const high of [false,true]){const ref=path.join(base,'route_probe/native_stills',`bobbleheads_faces_${high?'large_':''}${c.native}.png`),b=await bbox(ref),s=b.h/c.face[3],left=Math.round(b.x+b.w/2-(c.face[0]+c.face[2]/2)*s),top=Math.round(b.y-c.face[1]*s);
   const w=Math.round(meta.width*s),h=Math.round(meta.height*s),buf=await sharp(input).resize(w,h).png().toBuffer();
   const sx=Math.max(0,-left),sy=Math.max(0,-top),dx=Math.max(0,left),dy=Math.max(0,top),cut=await sharp(buf).extract({left:sx,top:sy,width:Math.min(w-sx,b.W-dx),height:Math.min(h-sy,b.H-dy)}).png().toBuffer();
   const result=await sharp({create:{width:b.W,height:b.H,channels:4,background:'#00000000'}}).composite([{input:cut,left:dx,top:dy}]).png().toBuffer();
   const out=path.join(base,outputDir,'assets/ui/characters',def.portrait,'stills/bobbleheads/faces',high?'large':'',def.portrait+'.png');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,result);
   const eyeY=top+c.eyes[1]*s,ratio=b.H/138;assert(eyeY>=61*ratio&&eyeY<=113*ratio,`${c.id}: eyes outside native court clip`);
   rows.push({id:c.id,high,reference:ref,canvas:[b.W,b.H],nativeFaceBox:b,eyeY,visible:true});
   if(!high){const prev=path.join(base,'assets_src_v2/ui/characters',def.portrait,'stills/bobbleheads',def.portrait+'.png');for(const src of [prev,result])tiles.push(await sharp(src).extract({left:0,top:61,width:84,height:52}).resize(252,156).png().toBuffer());}
  }
 }
 if(old){console.log(JSON.stringify({check:'native court clip',rows,pass:rows.every(r=>r.visible)}));process.exitCode=rows.every(r=>r.visible)?0:1;return;}
 const out=path.join(base,outputDir);fs.writeFileSync(path.join(out,'alignment_check.json'),JSON.stringify({ui:'court_screen_info_lists.twui.xml: portrait offset y=-61, bobbleheads 84x138',rows,runtime_passed:false},null,2));
 await sharp({create:{width:504,height:cases.length*156,channels:4,background:'#303030'}}).composite(tiles.map((input,i)=>({input,left:(i%2)*252,top:Math.floor(i/2)*156}))).png().toFile(path.join(out,'court_clip_before_after.png'));
 console.log(`PASS: ${rows.length} bobblehead files aligned; native court clip preview generated.`);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
