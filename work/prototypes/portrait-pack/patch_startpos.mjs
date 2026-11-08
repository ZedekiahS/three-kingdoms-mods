// Reuse the workspace CAAB reader. Only fixed-width string references inside
// target PERSISTENT_CHARACTER/CHARACTER_ART_SET_INFO records are changed.
import fs from 'node:fs';
import {readCaabHeader,parseCaabStringTables,walkCaabNodes} from './caabOffsets.mjs';
const [input,output,mappingFile]=process.argv.slice(2);
const mapping=JSON.parse(fs.readFileSync(mappingFile,'utf8'));
const original=fs.readFileSync(input),b=Buffer.from(original),h=readCaabHeader(b),t=parseCaabStringTables(b,h.recordNamesOffset);
const stack=[],changes=[],additions=[];let current=null,nextId=Math.max(...t.utf8ById.keys())+1;
const ids=new Map([...t.utf8ById].map(([id,s])=>[s,id]));
function idFor(s){if(!ids.has(s)){ids.set(s,nextId++);additions.push({id:ids.get(s),text:s});}return ids.get(s);}
walkCaabNodes(b,h,t,{
 onRecordStart:r=>{stack.push(r.name);if(r.name==='PERSISTENT_CHARACTER')current={template:null,arts:[]};},
 onValue:v=>{if(!current)return;if(stack.at(-1)==='PERSISTENT_CHARACTER'&&mapping[v.value?.text])current.template=v.value.text;if(stack.at(-1)==='CHARACTER_ART_SET_INFO'&&v.type==='ascii'&&v.value.text.includes('_art_set_'))current.arts.push(v);},
 onRecordEnd:()=>{if(stack.at(-1)==='PERSISTENT_CHARACTER'){
  if(current.template){if(current.arts.length!==1)throw Error('Expected exactly one art binding: '+current.template);const v=current.arts[0],replacement=mapping[current.template];if(v.marker!==15)throw Error('Expected ASCII reference');b.writeUInt32LE(idFor(replacement),v.offset+1);changes.push({template:current.template,old:v.value.text,new:replacement,offset:v.offset+1});}
  current=null;
 }stack.pop();}
});
const first=t.entries.find(e=>e.table==='utf8');if(!first)throw Error('Missing ASCII table');
const countOffset=first.offset-6;b.writeUInt32LE(t.utf8ById.size+additions.length,countOffset);
const tail=additions.map(e=>{const s=Buffer.from(e.text),n=Buffer.alloc(2),id=Buffer.alloc(4);n.writeUInt16LE(s.length);id.writeUInt32LE(e.id);return Buffer.concat([n,s,id]);});
const result=Buffer.concat([b,...tail]);
// Every original byte outside the specific reference fields and table count stays identical.
const allowed=new Set();for(const c of changes)for(let i=0;i<4;i++)allowed.add(c.offset+i);for(let i=0;i<4;i++)allowed.add(countOffset+i);
for(let i=0;i<b.length;i++)if(b[i]!==original[i]&&!allowed.has(i))throw Error('Unexpected byte mutation');
const verifyTables=parseCaabStringTables(result,h.recordNamesOffset);let verified=0;
walkCaabNodes(result,h,verifyTables,{onValue:v=>{if(changes.some(c=>c.offset===v.offset+1)){if(v.value.text!==changes.find(c=>c.offset===v.offset+1).new)throw Error('Readback mismatch');verified++;}}});
if(verified!==changes.length)throw Error('Readback count mismatch');fs.writeFileSync(output,result);
console.log(JSON.stringify({changes,addedStrings:additions.length,unchangedNonTargetBytes:true,readbackVerified:verified}));
