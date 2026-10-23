"use strict";
// Educational UI reducer for a streaming assistant; frontend hiding isn't authz.
// A trusted server must independently authorize every source and tool action.
const MAX=8192;
function initial(){return {owner:null,request:null,epoch:0,status:"idle",text:"",citations:[],error:null};}
function transition(previous,event){
  const s={...previous};
  if(event.type==="logout")return {...initial(),epoch:s.epoch+1};
  if(event.type==="start"){
    if(typeof event.owner!=="string"||!event.owner||typeof event.request!=="string"||!event.request)
      throw new Error("session/request identity required");
    return {owner:event.owner,request:event.request,epoch:s.epoch+1,
            status:"streaming",text:"",citations:[],error:null};
  }
  if(event.epoch!==s.epoch||event.owner!==s.owner||event.request!==s.request||s.status!=="streaming")
    return s; // late/out-of-order chunk from cancelled or previous session
  if(event.type==="token"){
    if(typeof event.value!=="string"||s.text.length+event.value.length>MAX)
      throw new Error("unbounded or invalid stream chunk");
    return {...s,text:s.text+event.value};
  }
  if(event.type==="complete"){
    if(!Array.isArray(event.citations)||event.citations.some(x=>typeof x!=="string"||!/^[-\w:]+$/.test(x)))
      throw new Error("invalid cited source ID");
    return {...s,status:"complete",citations:event.citations.slice()};
  }
  if(event.type==="cancel")return {...s,epoch:s.epoch+1,status:"cancelled"};
  if(event.type==="error")return {...s,status:"error",error:String(event.message||"request failed")};
  return s;
}
function check(){
  const assert=require("node:assert/strict");
  let s=transition(initial(),{type:"start",owner:"A",request:"r1"});
  const old=s.epoch;
  s=transition(s,{type:"token",owner:"A",request:"r1",epoch:old,value:"Answer"});
  assert.equal(s.text,"Answer");
  s=transition(s,{type:"start",owner:"B",request:"r2"});
  s=transition(s,{type:"token",owner:"A",request:"r1",epoch:old,value:" PRIVATE"});
  assert.equal(s.text,"");
  assert.equal(s.owner,"B");
  const current=s.epoch;
  s=transition(s,{type:"token",owner:"B",request:"r2",epoch:current,value:"Public"});
  s=transition(s,{type:"complete",owner:"B",request:"r2",epoch:current,citations:["B:1"]});
  assert.deepEqual(s.citations,["B:1"]);
  s=transition(s,{type:"logout"});
  assert.equal(s.text,"");
  assert.equal(s.owner,null);
  assert.deepEqual(s.citations,[]);
  assert.throws(()=>transition(transition(initial(),{type:"start",owner:"X",request:"z"}),
               {type:"token",owner:"X",request:"z",epoch:1,value:"a".repeat(MAX+1)}));
  console.log("Frontend reducer: stale async chunks, owner isolation, logout, source IDs, limit PASS");
}
if(require.main===module)check();
module.exports={initial,transition,check};
