/* Graded fixtures, local evidence, and bounded Worker runs. */
(async () => {
  'use strict';
  const {store, model} = window.GuideStudy;
  await store.ready;
  const ROOT = new URL('./', document.currentScript?.src || new URL('practice.js', location.href));
  const data = window.GUIDE_PRACTICE;
  const touched = new Set();
  document.querySelectorAll('[data-hint], [data-solution]').forEach(details => details.addEventListener('toggle', () => {
    if (details.open) touched.add(details.closest('[data-assessment], [data-lab]').id);
  }));
  document.querySelectorAll('[data-assessment]').forEach(card => {
    const item = data.assessments.find(a => a.id === card.dataset.assessment);
    const button = card.querySelector('[data-grade]'); button.disabled = false;
    button.addEventListener('click', async () => {
      const feedback = card.querySelector('[data-feedback]');
      let passed = null, summary = '';
      if (item.kind === 'self-review') {
        summary = card.querySelector('[data-design]').value.trim();
        if (!summary) { feedback.textContent = 'Write your design before recording a self-review.'; return; }
        feedback.textContent = 'Self-review recorded. Compare each requirement with the rubric and model answer; this is not an automated grade.';
      } else {
        const chosen = card.querySelector('input:checked');
        if (!chosen) { feedback.textContent = 'Choose an answer first.'; return; }
        const option = item.options.find(o => o.id === chosen.value);
        passed = chosen.value === item.correct; summary = option.feedback;
        feedback.textContent = (passed ? 'Passed. ' : 'Not yet. ') + option.feedback + ' ' + item.explanation;
      }
      button.disabled = true;
      try {
        await store.recordAttempt({topic:item.topic, assessment:item.id, kind:item.kind, passed, independent:item.independent, hintsUsed:touched.has(card.id), summary:summary.slice(0,2000)});
      } finally { button.disabled = false; }
    });
  });
  function order() {
    const container = document.querySelector('#assessment-cards');
    if (!container) return;
    const sourceOrder = new Map(data.assessments.map((item,index) => [item.id,index]));
    let cards = [...container.children].sort((a,b) => sourceOrder.get(a.dataset.assessment)-sourceOrder.get(b.dataset.assessment));
    if (document.querySelector('#practice-order').value === 'seeded') cards = model.seeded(cards, document.querySelector('#practice-seed').value);
    else {
      const attempts = store.snapshot.attempts;
      const rank = card => {
        const last = attempts.filter(a => a.assessment === card.dataset.assessment).at(-1);
        if (last?.passed === false) return 0;
        if ((store.snapshot.reviews[card.dataset.topic]?.nextReview || Infinity) <= Date.now()) return 1;
        return last ? 3 : 2;
      };
      cards.sort((a,b) => rank(a) - rank(b));
    }
    container.append(...cards);
  }
  document.querySelector('#order-practice')?.addEventListener('click', order);
  order();
  document.querySelectorAll('[data-lab]').forEach(card => {
    const item = data.labs.find(lab => lab.id === card.dataset.lab);
    const editor = card.querySelector('textarea'), run = card.querySelector('[data-run]'), stop = card.querySelector('[data-stop]');
    const status = card.querySelector('[data-lab-status]'), output = card.querySelector('[data-lab-output]');
    let active, timer;
    function finish() { clearTimeout(timer); active?.terminate(); active = undefined; run.disabled = false; stop.disabled = true; }
    async function record(passed, summary) {
      await store.recordAttempt({topic:item.topic, assessment:item.id, kind:'coding', passed, independent:true, hintsUsed:touched.has(card.id), summary:summary.slice(0,2000)});
    }
    run.disabled = !('Worker' in window);
    if (run.disabled) status.textContent = 'This browser does not support Workers. Download and run the local source instead.';
    stop.addEventListener('click', () => { finish(); status.textContent = 'Stopped. No completed test result was recorded.'; });
    card.querySelector('[data-reset]').addEventListener('click', () => {
      finish(); editor.value = item.starter; output.textContent = ''; status.textContent = 'Starter restored. Hint and solution use remains recorded for this session.';
    });
    run.addEventListener('click', () => {
      if (editor.value.length > 64000) { status.textContent = 'Source exceeds the 64,000-character limit.'; return; }
      finish(); run.disabled = true; stop.disabled = false; output.textContent = '';
      status.textContent = item.language === 'python' ? 'Loading the local Python runtime…' : 'Running in a disposable Worker…';
      const ticket = crypto.randomUUID();
      try { active = new Worker(new URL('lab-worker.js', ROOT)); }
      catch (error) { finish(); status.textContent = 'Worker could not start. Open this site over HTTP(S), or use the local download.'; return; }
      const worker = active;
      const timeout = () => {
        finish(); status.textContent = 'Time limit reached. Worker terminated; simplify the program or check for an infinite loop.';
        record(false, 'Execution timed out').catch(() => {});
      };
      timer = setTimeout(timeout, item.language === 'python' ? 30000 : 3000);
      worker.onerror = event => { event.preventDefault(); finish(); status.textContent = 'Runtime could not start. Python requires the runtime folder; use the local download if it is unavailable.'; };
      worker.onmessage = async event => {
        if (worker !== active || event.data.ticket !== ticket) return;
        const message = event.data;
        if (message.type === 'ready') { clearTimeout(timer); timer = setTimeout(timeout, 3000); status.textContent = 'Runtime ready; executing tests…'; return; }
        finish();
        if (message.type === 'error') {
          output.textContent = String(message.output || '') + '\n' + message.message;
          status.textContent = 'Execution failed. Check the error or use the local source if the optional runtime is missing.';
          await record(false, message.message); return;
        }
        if (message.type !== 'result') return;
        const passed = message.results.length === item.cases.length && message.results.every(result => result.passed);
        const count = message.results.filter(result => result.passed).length;
        status.textContent = `${passed ? 'Passed' : 'Not yet'}: ${count}/${item.cases.length} tests. ${touched.has(card.id) ? 'Assisted attempt.' : 'Independent fixture attempt.'}`;
        output.textContent = message.results.map(result => `${result.passed ? 'PASS' : 'FAIL'} ${result.name}${result.passed ? '' : ': '+(result.error || `expected ${result.expected}; received ${result.actual}`)}`).join('\n') + '\n\n' + String(message.output || '');
        await record(passed, `${count}/${item.cases.length} tests passed`);
      };
      worker.postMessage({ticket, code:editor.value, cases:item.cases, language:item.language, runtimeURL:new URL('runtime/pyodide/', ROOT).href});
    });
  });
  function renderStudy() {
    const summary = document.querySelector('#study-summary');
    if (!summary || !window.GUIDE_TOPICS) return;
    const state = store.snapshot, topics = new Map(window.GUIDE_TOPICS.map(topic => [String(topic.id), topic]));
    const counts = {Familiar:0, Practiced:0, Independent:0, Mastered:0};
    for (const id of topics.keys()) { const stage = model.mastery(state,id).stage; if (stage in counts) counts[stage]++; }
    summary.textContent = Object.entries(counts).map(([stage,count]) => `${count} ${stage}`).join(' · ') + ` · ${state.attempts.length} attempts`;
    const due = document.querySelector('#study-due'); due.replaceChildren();
    const heading = document.createElement('h2'); heading.textContent = 'Due for review'; due.append(heading);
    const dueIds = Object.keys(state.reviews).filter(id => state.reviews[id].nextReview <= Date.now() && topics.has(id));
    if (!dueIds.length) { const empty = document.createElement('p'); empty.textContent = 'Nothing due. Try a new assessment or coding lab.'; due.append(empty); }
    for (const id of dueIds) {
      const paragraph = document.createElement('p'), link = document.createElement('a');
      link.href = new URL(topics.get(id).url, ROOT); link.textContent = topics.get(id).title; paragraph.append(link); due.append(paragraph);
    }
    const history = document.querySelector('#study-history'); history.replaceChildren();
    const title = document.createElement('h2'); title.textContent = 'Recent attempts'; history.append(title);
    const list = document.createElement('ol');
    for (const attempt of [...state.attempts].reverse().slice(0,100)) {
      const li = document.createElement('li');
      li.textContent = `${new Date(attempt.time).toLocaleString()} · ${attempt.assessment} · ${attempt.passed === null ? 'self-review' : attempt.passed ? 'passed' : 'not yet'}${attempt.hintsUsed ? ' · assisted' : ''}: ${attempt.summary}`;
      list.append(li);
    }
    history.append(list);
  }
  store.addEventListener('change', renderStudy); renderStudy();
  window.GuidePracticeReady = true;
})();
