const ui = {draft: 'first question', expanded: false};
const tasks = new Map([['T1', {status: 'completed', answer: 'saved answer'}]]);
ui.draft = 'new question';
console.log(tasks.get('T1').answer);
