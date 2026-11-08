import fs from 'node:fs';
import {readCaabHeader,parseCaabStringTables,walkCaabNodes} from '../trait_readout/caabBinary.mjs';
const b=fs.readFileSync(process.argv[2]),h=readCaabHeader(b),t=parseCaabStringTables(b,h.recordNamesOffset),path=[];
let compression={},refs=new Set();
walkCaabNodes(b,h,t,{
  onRecordStart:r=>path.push(r.name),onRecordEnd:()=>path.pop(),
  onValue:v=>{
    if(path.at(-1)==='COMPRESSED_DATA'&&v.kind==='array')compression.payload={offset:v.value.payloadOffset,length:v.value.payloadByteLength};
    if(path.at(-1)==='COMPRESSED_DATA_INFO'){
      if(v.type==='u32'){
        // Three Kingdoms CAAB marker 0x18 stores uint24 big-endian.
        // The reused WH3 reader returns LE for this marker; adapt only this size field.
        compression.size=v.marker===0x18?((v.value&255)<<16)|(v.value&65280)|((v.value>>>16)&255):v.value;
      }
      if(v.kind==='array')compression.props={offset:v.value.payloadOffset,length:v.value.payloadByteLength};
    }
    const value=v.value?.text;
    if(path.at(-1)==='PERSISTENT_CHARACTER'&&typeof value==='string'&&value.includes('_template_'))refs.add(value);
  }
});
console.log(JSON.stringify({compression,templates:[...refs].sort()}));
