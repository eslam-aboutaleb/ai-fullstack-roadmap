/* Browser-only interactions; core content remains readable without JavaScript. */
(() => {
  'use strict';
  const KEY = 'ai-fullstack-roadmap-v1';
  const QUESTION_COUNT = Number(document.body.dataset.questionCount) || 0;
  let state = { learned: {}, bookmarks: {}, notes: {}, theme: 'light' };
  let storageOK = true;
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || localStorage.getItem('ragnor-learning-v1') || 'null');
    if (saved && typeof saved === 'object') state = validate(saved);
  } catch { storageOK = false; }
  function validate(input) {
    const out = { learned: {}, bookmarks: {}, notes: {}, theme: input.theme === 'light' ? 'light' : 'dark' };
    for (let id = 1; id <= QUESTION_COUNT; id++) {
      if (input.learned?.[id] === true) out.learned[id] = true;
      if (input.bookmarks?.[id] === true) out.bookmarks[id] = true;
      if (typeof input.notes?.[id] === 'string') out.notes[id] = input.notes[id].slice(0, 20000);
    }
    return out;
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); }
    catch { storageOK = false; }
    updateProgress();
  }
  function updateProgress() {
    const total = Object.values(state.learned).filter(Boolean).length;
    const bar = document.querySelector('#progress');
    if (bar) bar.value = total;
    const label = document.querySelector('#progress-label');
    if (label) label.textContent = `${total} / ${QUESTION_COUNT} topics understood`;
    const storage = document.querySelector('#storage-status');
    if (storage && !storageOK) storage.textContent = 'Browser storage is unavailable. Changes last for this page session; export a backup.';
  }
  function syncControls() {
    document.documentElement.dataset.theme = state.theme;
    document.querySelectorAll('[data-learned]').forEach(el => { el.checked = !!state.learned[el.dataset.learned]; });
    document.querySelectorAll('[data-bookmark]').forEach(el => {
      const on = !!state.bookmarks[el.dataset.bookmark];
      el.setAttribute('aria-pressed', String(on));
      el.textContent = on ? 'Bookmarked' : 'Bookmark';
    });
    document.querySelectorAll('[data-note]').forEach(el => { el.value = state.notes[el.dataset.note] || ''; });
    updateProgress();
  }
  syncControls();
  document.querySelector('#theme')?.addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = state.theme;
    save();
  });
  document.querySelectorAll('[data-learned]').forEach(el => el.addEventListener('change', () => {
    state.learned[el.dataset.learned] = el.checked; save();
  }));
  document.querySelectorAll('[data-bookmark]').forEach(el => el.addEventListener('click', () => {
    const id = el.dataset.bookmark;
    state.bookmarks[id] = !state.bookmarks[id]; save(); syncControls();
  }));
  document.querySelectorAll('[data-note]').forEach(el => el.addEventListener('input', () => {
    state.notes[el.dataset.note] = el.value.slice(0, 20000); save();
  }));
  document.querySelectorAll('.copy').forEach(el => el.addEventListener('click', async () => {
    const text = el.parentElement.querySelector('code').textContent;
    try { await navigator.clipboard.writeText(text); el.textContent = 'Copied'; }
    catch {
      const range = document.createRange(); range.selectNodeContents(el.parentElement.querySelector('code'));
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      el.textContent = 'Selected — copy with your keyboard';
    }
  }));
  let practicing = new URLSearchParams(location.search).get('mode') === 'practice';
  function practice(on) {
    practicing = on;
    document.body.classList.toggle('practice', on);
    document.querySelectorAll('.answer').forEach(el => { el.open = !on; });
    const button = document.querySelector('#practice');
    if (button) { button.textContent = on ? 'Reading mode: reveal answers' : 'Practice: hide answers'; button.setAttribute('aria-pressed', String(on)); }
  }
  if (practicing) practice(true);
  document.querySelector('#practice')?.addEventListener('click', () => practice(!practicing));
  document.querySelector('#expand')?.addEventListener('click', () => practice(false));
  const all = window.GUIDE_SEARCH || [];
  const query = document.querySelector('#query');
  const chapter = document.querySelector('#chapter-filter');
  const status = document.querySelector('#status-filter');
  const results = document.querySelector('#results');
  let visibleResults = 20;
  function search(reset = true) {
    if (reset) visibleResults = 20;
    if (!results) return;
    const terms = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const filtered = all.filter(q => {
      const text = q.text.toLocaleLowerCase();
      const selected = status.value;
      return (!chapter.value || q.slug === chapter.value) && terms.every(term => text.includes(term)) &&
        (selected === 'all' || selected === 'learned' && state.learned[q.id] || selected === 'unlearned' && !state.learned[q.id] || selected === 'bookmarked' && state.bookmarks[q.id]);
    });
    results.replaceChildren();
    document.querySelector('#search-count').textContent = `${filtered.length} matching question${filtered.length === 1 ? '' : 's'}`;
    if (!filtered.length) {
      const message = document.createElement('p'); message.textContent = 'No questions match these filters. Try fewer words or another chapter.'; results.append(message);
    }
    for (const q of filtered.slice(0, visibleResults)) {
      const link = document.createElement('a'); link.className = 'result'; link.href = `${q.slug}.html#q${q.id}`;
      const title = document.createElement('strong'); title.textContent = q.title;
      const meta = document.createElement('small'); meta.textContent = `${q.type || "Topic"} · ${q.chapter}${state.learned[q.id] ? ' · learned' : ''}${state.bookmarks[q.id] ? ' · bookmarked' : ''}`;
      const excerpt = document.createElement('span'); excerpt.className = 'snippet';
      const pos = terms.length ? Math.max(0, q.text.toLocaleLowerCase().indexOf(terms[0]) - 65) : q.title.length + 1;
      excerpt.textContent = (pos ? '…' : '') + q.text.slice(pos, pos + 210) + '…';
      link.append(meta, title, excerpt); results.append(link);
    }
    const more = document.querySelector("#more-results");
    if (more) more.hidden = visibleResults >= filtered.length;
  }
  document.querySelector('#more-results')?.addEventListener('click', () => { visibleResults += 20; search(false); });
  query?.addEventListener('input', search); chapter?.addEventListener('change', search); status?.addEventListener('change', search); search();
  document.querySelector('#random')?.addEventListener('click', () => {
    const pending = all.filter(q => !state.learned[q.id]);
    const pool = pending.length ? pending : all;
    const q = pool[Math.floor(Math.random() * pool.length)];
    if (q) location.href = `${q.slug}.html?mode=practice#q${q.id}`;
  });
  document.querySelector('#term-search')?.addEventListener('input', event => {
    const term = event.target.value.toLocaleLowerCase().trim();
    document.querySelectorAll('[data-term]').forEach(el => { el.hidden = !el.dataset.term.includes(term); });
  });
  document.addEventListener('keydown', event => {
    if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey || ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) return;
    event.preventDefault();
    if (query) { query.focus(); query.scrollIntoView({ block: 'center' }); }
    else location.href = 'index.html#search';
  });
  document.querySelector('#export')?.addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify({ version: 1, ...state }, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = 'ai-fullstack-study-progress.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  document.querySelector('#import')?.addEventListener('change', async event => {
    const file = event.target.files[0]; if (!file) return;
    const message = document.querySelector('#storage-status');
    try {
      if (file.size > 32000000) throw new Error('File is too large.');
      const data = JSON.parse(await file.text());
      if (!data || data.version !== 1 || typeof data.learned !== 'object' || typeof data.notes !== 'object') throw new Error('Choose a version 1 handbook progress export.');
      const incoming = validate(data);
      // Merge so importing an older backup does not erase newer local study.
      state = { theme: incoming.theme, learned: { ...state.learned, ...incoming.learned }, bookmarks: { ...state.bookmarks, ...incoming.bookmarks }, notes: { ...state.notes, ...incoming.notes } };
      save(); syncControls(); search(); message.textContent = storageOK ? 'Progress imported and merged with this browser.' : 'Imported for this session. Browser storage is unavailable; keep your export.';
    } catch (err) { message.textContent = `Import failed: ${err.message}`; }
    event.target.value = '';
  });
  window.addEventListener('storage', event => {
    if (event.key !== KEY || !event.newValue) return;
    try { state = validate(JSON.parse(event.newValue)); syncControls(); search(); } catch { /* Ignore malformed external changes. */ }
  });
})();
