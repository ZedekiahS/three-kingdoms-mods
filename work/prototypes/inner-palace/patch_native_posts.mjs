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
}else{throw new Error('Only wrap mode is included in the portrait repository');}
