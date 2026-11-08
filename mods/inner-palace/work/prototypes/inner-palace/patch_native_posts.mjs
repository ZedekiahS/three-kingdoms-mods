// Local 3K CAAB adaptation. Reads with the existing WH3-Mod-Manager-derived
// parser; record/group encoding follows RPFM's documented CAAB length format.
// No game script API is invented. Original input files are never overwritten.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {readCaabHeader,parseCaabStringTables,walkCaabNodes} from '../../../trait_readout/caabBinary.mjs';

function variable(b,p){let n=0;while(true){const x=b[p++];n=n*128+(x&127);if(!(x&128))return [n,p];}}
function sized(n,width=0){let a=[n%128];while(n=Math.floor(n/128))a.unshift((n%128)|128);while(a.length<width)a.unshift(128);return Buffer.from(a);}
function u32(n){const b=Buffer.alloc(4);b.writeUInt32LE(n);return b;}
function uint(n){return Buffer.concat([Buffer.from([8]),u32(n)]);}
function record(prefix,groups,array){const content=Buffer.concat(groups.map(g=>array?Buffer.concat([sized(g.length),g]):g));return Buffer.concat([prefix,sized(content.length),...(array?[sized(groups.length)]:[]),content]);}

function load(b){
 const header=readCaabHeader(b),tables=parseCaabStringTables(b,header.recordNamesOffset),stack=[],records=[];let root;
 walkCaabNodes(b,header,tables,{
  onRecordStart(r){
   const n={...r,groups:[],values:[],cursor:r.blockStartOffset};records.push(n);
   const prefixLength=((r.flags&32)||!stack.length)?4:2;n.prefix=b.subarray(r.startOffset,r.startOffset+prefixLength);
   const lengthStart=r.startOffset+prefixLength,lengthEnd=variable(b,lengthStart)[1];n.sizeWidth=lengthEnd-lengthStart;n.countWidth=r.blockStartOffset-lengthEnd;
   if(stack.length)stack.at(-1).groups.at(-1).children.push(n);else root=n;
   if(!(r.flags&64))n.groups.push({start:r.blockStartOffset,end:r.blockEndOffset,children:[]});
   stack.push(n);
  },onRecordEnd(){stack.pop();},
  onGroupStart(){const n=stack.at(-1),[size,start]=variable(b,n.cursor);n.groups.push({start,end:start+size,width:start-n.cursor,children:[]});n.cursor=start+size;},
  onValue(v){stack.at(-1).values.push(v);}
 });
 function render(n){
  if(n.replacement)return n.replacement;
  const groups=n.groups.map(g=>{let p=g.start,a=[];for(const c of g.children){a.push(b.subarray(p,c.startOffset),render(c));p=c.blockEndOffset;}a.push(b.subarray(p,g.end));return Buffer.concat(a);});
  groups.push(...(n.appendGroups??[]));
  const array=!!(n.flags&64),content=Buffer.concat(groups.map((g,i)=>array?Buffer.concat([sized(g.length,n.groups[i]?.width??0),g]):g));
  return Buffer.concat([n.prefix,sized(content.length,n.sizeWidth),...(array?[sized(groups.length,n.countWidth)]:[]),content]);
 }
 function output(tail=b.subarray(header.recordNamesOffset)){const body=render(root),h=Buffer.from(b.subarray(0,16));h.writeUInt32LE(16+body.length,12);return Buffer.concat([h,body,tail]);}
 assert(output().equals(b),'Unedited CAAB roundtrip must be byte-identical');
 return {b,header,tables,records,root,output};
}

const [mode,input,output,arg]=process.argv.slice(2);assert(input!==output);
const model=load(fs.readFileSync(input)),{b,tables,records}=model;
if(mode==='wrap'){
 const payload=fs.readFileSync(arg),info=records.find(r=>r.name==='COMPRESSED_DATA_INFO'),container=records.find(r=>r.name==='COMPRESSED_DATA');assert(info&&container);
 const size=Number(process.argv[6]);assert(Number.isSafeInteger(size)&&size>0);
 const props=payload.subarray(0,5),compressed=payload.subarray(13);
 const array=x=>Buffer.concat([Buffer.from([0x46]),sized(x.length),x]);
 const infoBytes=record(info.prefix,[Buffer.concat([uint(size),array(props)])],false);
 container.replacement=record(container.prefix,[Buffer.concat([array(compressed),infoBytes])],false);
 fs.writeFileSync(output,model.output());console.log(JSON.stringify({mode,size,compressed:compressed.length}));
}else{
 assert.equal(mode,'posts');
 const keys=JSON.parse(fs.readFileSync(arg,'utf8')).posts.map(p=>p[0]);assert([5,14].includes(keys.length));assert.equal(new Set(keys).size,keys.length);
 const posts=records.filter(r=>r.name==='CHARACTER_POST');
 const ids=posts.map(r=>r.values[0].value);assert.equal(new Set(ids).size,ids.length);
 const queue=records.find(r=>r.name==='CAMPAIGN_COMMAND_QUEUE_INDEX_TABLES');
 // Verified against both local 190 historical and 194 romance startpos:
 // index 15 is the post allocation counter, two above the highest live post ID.
 const oldCounter=queue.values[15].value;assert.equal(oldCounter,Math.max(...ids)+2);
 let next=oldCounter;
 const factions=records.filter(r=>r.name==='FACTION');
 const allowed=new Set(process.argv[6]?JSON.parse(fs.readFileSync(process.argv[6],'utf8')):['3k_main_faction_lu_bu']);
 const targets=factions.filter(r=>allowed.has(r.values[1]?.value?.text));assert(targets.length>0);
 const targetNames=new Set(targets.map(r=>r.values[1].value.text));
 const lists=targets.flatMap(f=>{
  const found=records.filter(r=>r.startOffset>f.startOffset&&r.blockEndOffset<f.blockEndOffset&&/^CHARACTER_POSTS_(CURRENT|OPPOSITE)_GOVERNMENT$/.test(r.name));
  assert.equal(found.length,2,'Expected current/opposite post lists for '+f.values[1].value.text);
  return found;
 });
 const sample=posts.find(r=>r.values.length===2&&r.groups.every(g=>g.children.length===0));assert(sample);
 const stringType=sample.values[1].marker;assert([14,15].includes(stringType));
 const targetTable=stringType===15?tables.utf8ById:tables.utf16ById;
 let stringNext=Math.max(...targetTable.keys())+1;
 const newStrings=keys.map(key=>({key,id:stringNext++}));assert(keys.every(key=>![...targetTable.values()].includes(key)));
 for(const list of lists){list.appendGroups=newStrings.map(({id})=>record(sample.prefix,[Buffer.concat([uint(next++),Buffer.from([stringType]),u32(id)])],false));}
 // Queue has only uint primitives. Re-encode just its counter; retain every
 // other byte, including optimized integer forms.
 let cursor=queue.blockStartOffset;
 for(let i=0;i<15;i++){const m=b[cursor];assert(m>=0x14&&m<=0x18);cursor+=1+([0,0,1,2,3][m-0x14]);}
 const oldWidth=1+([0,0,1,2,3][b[cursor]-0x14]);assert(oldWidth>0);
 queue.replacement=record(queue.prefix,[Buffer.concat([b.subarray(queue.blockStartOffset,cursor),uint(next),b.subarray(cursor+oldWidth,queue.blockEndOffset)])],false);
 // Keep existing string IDs and order; append only our independent post keys.
 let p=model.header.recordNamesOffset,n=b.readUInt16LE(p);p+=2;
 for(let i=0;i<n;i++){let len=b.readUInt16LE(p);p+=2+len;}
 const utf16CountAt=p;n=b.readUInt32LE(p);p+=4;
 for(let i=0;i<n;i++){let len=b.readUInt16LE(p);p+=2+len*2+4;}
 const utf8CountAt=p;n=b.readUInt32LE(p);p+=4;
 for(let i=0;i<n;i++){let len=b.readUInt16LE(p);p+=2+len+4;}assert.equal(p,b.length);
 const strings=Buffer.concat(newStrings.map(({key,id})=>{const text=Buffer.from(key,stringType===15?'utf8':'utf16le'),len=Buffer.alloc(2);len.writeUInt16LE(key.length);return Buffer.concat([len,text,u32(id)]);}));
 const countAt=stringType===15?utf8CountAt:utf16CountAt,end=stringType===15?b.length:utf8CountAt;
 const tail=Buffer.concat([b.subarray(model.header.recordNamesOffset,countAt),u32(b.readUInt32LE(countAt)+keys.length),b.subarray(countAt+4,end),strings,b.subarray(end)]);
 const patched=model.output(tail),check=load(patched);
 const afterPosts=check.records.filter(r=>r.name==='CHARACTER_POST');assert.equal(afterPosts.length,posts.length+keys.length*lists.length);
 const afterIds=afterPosts.map(r=>r.values[0].value);assert.equal(afterIds.length,new Set(afterIds).size);
 assert.equal(check.records.find(r=>r.name===queue.name).values[15].value,next);
 for(const key of keys)assert.equal(afterPosts.filter(r=>r.values[1]?.value?.text===key).length,lists.length);
 // Check every targeted faction and both governments, not only total counts.
 for(const f of check.records.filter(r=>r.name==='FACTION'&&targetNames.has(r.values[1]?.value?.text))){
  const found=check.records.filter(r=>r.startOffset>f.startOffset&&r.blockEndOffset<f.blockEndOffset&&/^CHARACTER_POSTS_(CURRENT|OPPOSITE)_GOVERNMENT$/.test(r.name));
  for(const list of found)for(const key of keys)assert.equal(afterPosts.filter(r=>r.startOffset>list.startOffset&&r.blockEndOffset<=list.blockEndOffset&&r.values[1]?.value?.text===key).length,1);
 }
 // Every pre-existing post and every excluded faction stays byte-identical.
 const originalPostData=posts.map(r=>b.subarray(r.startOffset,r.blockEndOffset).toString('hex'));
 const afterOriginal=afterPosts.filter(r=>!keys.includes(r.values[1]?.value?.text)).map(r=>patched.subarray(r.startOffset,r.blockEndOffset).toString('hex'));
 assert.deepEqual(afterOriginal,originalPostData);
 const otherBefore=factions.filter(r=>!targetNames.has(r.values[1]?.value?.text)).map(r=>b.subarray(r.startOffset,r.blockEndOffset).toString('hex'));
 const otherAfter=check.records.filter(r=>r.name==='FACTION'&&!targetNames.has(r.values[1]?.value?.text)).map(r=>patched.subarray(r.startOffset,r.blockEndOffset).toString('hex'));
 assert.deepEqual(otherAfter,otherBefore);
 fs.writeFileSync(output,patched);console.log(JSON.stringify({mode,factions:[...targetNames],keys,added:keys.length*lists.length,oldCounter,next,roundtrip:true,excludedFactionsUnchanged:true,originalPostsUnchanged:true}));
}
