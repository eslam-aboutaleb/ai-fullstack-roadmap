const state = {owner:'A',generation:1,text:''};
function apply(previous,event) {
  if (event.generation !== previous.generation) return previous;
  return {...previous,text:event.text};
}
const next = apply(state,{generation:0,text:'obsolete'});
if (next !== state) throw new Error('Stale response accepted');
console.log(next.text === '');

