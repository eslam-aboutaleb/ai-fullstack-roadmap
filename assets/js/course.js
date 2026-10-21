/* Deterministic teaching interactions. These do not invoke an AI model. */
(() => {
  'use strict';
  const menu = document.querySelector('#menu-toggle');
  const sidebar = document.querySelector('#navigation');
  function setMenu(open) {
    menu?.setAttribute('aria-expanded', String(open));
    sidebar?.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);
  }
  menu?.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.body.classList.contains('menu-open')) {
      setMenu(false); menu.focus();
    }
  });
  document.addEventListener('click', event => {
    if (document.body.classList.contains('menu-open') && !sidebar.contains(event.target) && event.target !== menu) setMenu(false);
  });
  document.querySelectorAll('[data-flow]').forEach(flow => {
    const steps = [...flow.querySelectorAll('[data-flow-step]')];
    let index = 0;
    const failure = flow.querySelector('[data-flow-failure]');
    const failButton = flow.querySelector('[data-flow-fail]');
    function select(next) {
      index = next;
      steps.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
      flow.querySelectorAll('[data-diagram-step]').forEach(node => node.classList.toggle('active', Number(node.dataset.diagramStep) === index));
      flow.querySelector('[data-flow-label]').textContent = `STEP ${index + 1} / ${steps[index].dataset.title}`;
      flow.querySelector('[data-flow-result]').textContent = steps[index].dataset.value;
      flow.querySelector('[data-flow-next]').textContent = index === steps.length - 1 ? 'Start again ↺' : 'Next step →';
      failure.hidden = true; failButton.setAttribute('aria-pressed', 'false');
    }
    steps.forEach((button, i) => {
      button.addEventListener('click', () => select(i));
      button.addEventListener('keydown', event => {
        if (!['ArrowRight', 'ArrowLeft'].includes(event.key)) return;
        event.preventDefault();
        select((i + (event.key === 'ArrowRight' ? 1 : steps.length - 1)) % steps.length);
        steps[index].focus();
      });
    });
    flow.querySelector('[data-flow-next]').addEventListener('click', () => select((index + 1) % steps.length));
    failButton.addEventListener('click', () => {
      failure.hidden = !failure.hidden;
      failButton.setAttribute('aria-pressed', String(!failure.hidden));
    });
  });
  const ragScenario = document.querySelector('#rag-scenario');
  if (ragScenario) {
    const fixtures = {
      supported: {status: 'ok', source: 'D7:r3', text: 'Sale items may be exchanged within 14 days. Refunds are not offered for sale items.', action: 'Explain that exchanges are allowed within 14 days, while this rule does not allow refunds for sale items. Cite D7:r3.', reason: 'The answer is constrained by the specific rule, including its exception.'},
      irrelevant: {status: 'ok', source: 'D9:r2', text: 'Delivery takes 3 to 5 days.', action: 'Do not answer the refund question from this passage. Search for an applicable rule or explain that this evidence is insufficient.', reason: 'Finding text is not the same as finding an answer to this question.'},
      missing: {status: 'ok', source: null, text: null, action: 'State that no supporting rule was found. Ask for a useful missing detail if it would narrow the search.', reason: 'A successful empty search does not justify inventing a rule.'},
      outage: {status: 'unavailable', source: null, text: null, action: 'Explain that the search could not be completed and offer retry. Do not claim the rule does not exist.', reason: 'An infrastructure failure and an empty result are different facts.'}
    };
    function updateRag() {
      const item = fixtures[ragScenario.value];
      document.querySelector('#rag-packet').textContent = JSON.stringify({question: 'Can I get a refund for a sale item?', retrieval_status: item.status, source: item.source, evidence: item.text}, null, 2);
      document.querySelector('#rag-action').textContent = item.action;
      document.querySelector('#rag-reason').textContent = item.reason;
    }
    ragScenario.addEventListener('change', updateRag); updateRag();
  }
  function revealTarget() {
    const target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    const moved = target.querySelector('[data-topic-redirect]');
    if (moved) { const destination = new URL(moved.href); destination.search = location.search; location.replace(destination.href); return; }
    if (new URLSearchParams(location.search).get('mode') === 'practice') return;
    target.querySelectorAll('details.answer').forEach(element => { element.open = true; });
  }
  // A same-fragment link does not emit hashchange; it must still reopen a closed answer.
  document.querySelectorAll('.finder-results a').forEach(link => link.addEventListener('click', () => {
    const target = document.getElementById(link.hash.slice(1));
    if (new URLSearchParams(location.search).get('mode') !== 'practice') {
      target?.querySelector('details.answer')?.setAttribute('open', '');
    }
  }));
  window.addEventListener('guide:ready', revealTarget);
  window.addEventListener('hashchange', revealTarget); revealTarget();
  try {
    const slug = document.body.dataset.page;
    if (slug) localStorage.setItem('ai-roadmap-reading-v1', JSON.stringify({slug, title: document.querySelector('h1').textContent}));
    const last = JSON.parse(localStorage.getItem('ai-roadmap-reading-v1') || 'null');
    const link = document.querySelector('#continue-reading');
    if (link && last && /^[a-z0-9-]+$/.test(last.slug)) {
      link.href = `${last.slug}.html`; link.textContent = `Continue: ${last.title}`;
    }
  } catch { /* Reading stays available without browser storage. */ }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        document.querySelectorAll('.lesson-toc a').forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      }
    }, {rootMargin: '-10% 0px -65% 0px'});
    document.querySelectorAll('.lesson').forEach(lesson => observer.observe(lesson));
  }
})();
