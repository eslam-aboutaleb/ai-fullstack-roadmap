const {simulate}=require('../assets/js/simulation-model.js');
console.log(JSON.stringify(['asyncio','locking','retrieval','retries'].map(id=>({id,normal:simulate(id),failure:simulate(id,true)}))));
