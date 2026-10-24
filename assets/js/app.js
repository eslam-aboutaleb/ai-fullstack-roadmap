/* Browser-only interactions; core content remains readable without JavaScript. */
(async () => {
  'use strict';
  const SITE_ROOT = new URL('./', document.currentScript.src);
  const TOPIC_COUNT = Number(document.body.dataset.topicCount) || 0;
  const QUESTION_COUNT = Number(document.body.dataset.questionCount) || 0;
  const THEMES = ['light', 'warm', 'dark'];
  const store = window.GuideStudy.store;
  await store.ready;
  let state = store.snapshot;
  // Navigation is the entry view. Focus is an explicit choice for this page,
  // rather than a saved preference that hides navigation on future visits.
  let focusMode = false;
  function save() {
    const previous = store.snapshot;
    const changes = [];
    for (const field of ['learned', 'bookmarks', 'notes', 'reviews', 'confidence']) {
      for (const [id, value] of Object.entries(state[field])) {
        if (JSON.stringify(previous[field][id]) !== JSON.stringify(value)) changes.push([field, id, value]);
      }
    }
    for (const field of ['theme']) if (previous[field] !== state[field]) changes.push([field, 'global', state[field]]);
    return Promise.all(changes.map(args => store.set(...args)));
  }

  function dueForReview() {
    const now = Date.now();
    return Object.entries(state.reviews).filter(([id, r]) => r.nextReview <= now).map(([id]) => Number(id));
  }

  function updateProgress() {
    const topics = new Set([...Object.keys(state.learned), ...state.attempts.map(attempt => String(attempt.topic))]);
    const stages = [...topics].filter(id => !QUESTION_COUNT || Number(id) <= QUESTION_COUNT).map(id => window.GuideStudyModel.mastery(state,id).stage);
    const total = stages.filter(stage => stage !== 'Not started').length;
    const bar = document.querySelector('#progress');
    if (bar) { bar.max = TOPIC_COUNT || QUESTION_COUNT; bar.value = total; }
    const label = document.querySelector('#progress-label');
    if (label) label.textContent = `${total} / ${TOPIC_COUNT || QUESTION_COUNT} topics started · ${stages.filter(stage => stage === 'Mastered').length} estimated mastered`;
    const due = dueForReview().length;
    const dueLabel = document.querySelector('#review-label');
    if (dueLabel) dueLabel.textContent = due ? `${due} due for review` : 'Nothing due for review';


    const storage = document.querySelector('#storage-status');
    if (storage) storage.textContent = store.status.warning || `Study record saved in ${store.status.backend}. No account or server sync; export to move devices.`;
  }

  function syncControls() {
  document.documentElement.dataset.theme = state.theme;
  document.body.classList.toggle('distraction-free', focusMode);
  const focusButton = document.querySelector('#distraction-free');
  if (focusButton) {
    focusButton.setAttribute('aria-pressed', String(focusMode));
    focusButton.textContent = focusMode ? 'Show sidebar' : 'Focus mode';
  }
  const themeBtn = document.querySelector('#theme');
    if (themeBtn) {
      const labels = { light: 'Theme: Light ☀️', warm: 'Theme: Warm ☕', dark: 'Theme: Dark 🌙' };
      themeBtn.textContent = labels[state.theme] || 'Change theme';
      themeBtn.title = 'Switch reading theme (Light → Warm Sepia → Dark)';
    }

    document.querySelectorAll('[data-bookmark]').forEach(el => {
      const on = !!state.bookmarks[el.dataset.bookmark];
      el.setAttribute('aria-pressed', String(on));
      el.textContent = on ? 'Bookmarked' : 'Bookmark';
    });
    document.querySelectorAll('[data-note]').forEach(el => { if (document.activeElement !== el || state.notes[el.dataset.note] === undefined) el.value = state.notes[el.dataset.note] || ''; });
    updateProgress();
  }

  store.addEventListener('change', () => { state = store.snapshot; syncControls(); });
  syncControls();

  document.querySelector('#theme')?.addEventListener('click', () => {
    const idx = THEMES.indexOf(state.theme);
    state.theme = THEMES[(idx + 1) % THEMES.length];
    document.documentElement.dataset.theme = state.theme;
    save();
    syncControls();
  });

  document.querySelector('#reset-progress')?.addEventListener('click', async () => {
    if (!window.confirm('Clear this browser’s notes, bookmarks, and practice history? Export a backup first.')) return;
    await store.clear();
    state = store.snapshot; syncControls(); search();
  });
  document.querySelectorAll('[data-bookmark]').forEach(el => el.addEventListener('click', () => {
    const id = el.dataset.bookmark;
    state.bookmarks[id] = !state.bookmarks[id]; save(); syncControls();
  }));
  document.querySelectorAll('[data-note]').forEach(el => el.addEventListener('input', () => {
    state.notes[el.dataset.note] = el.value.slice(0, 20000); save();
  }));

  const originalCode = new WeakMap();
  document.querySelectorAll('pre code').forEach(block => originalCode.set(block, block.textContent));
  document.querySelectorAll('.copy').forEach(el => el.addEventListener('click', async () => {
    const block = el.parentElement.querySelector('code');
    const text = originalCode.get(block) ?? block.textContent;
    try { await navigator.clipboard.writeText(text); el.textContent = 'Copied'; }
    catch {
      const range = document.createRange(); range.selectNodeContents(el.parentElement.querySelector('code'));
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      el.textContent = 'Selected — copy with your keyboard';
    }
  }));

  let practicing = true;
  function practice(on) {
    practicing = on;
    document.body.classList.toggle('practice', on);
    document.querySelectorAll('.answer').forEach(el => { el.open = !on; });
    const button = document.querySelector('#practice');
    for (const control of [button, document.querySelector('#expand')]) {
      if (control) { control.textContent = on ? 'View all answers' : 'Hide all answers'; control.setAttribute('aria-pressed', String(!on)); }
    }
  }
  if (practicing) practice(true);
  document.querySelector('#practice')?.addEventListener('click', () => practice(!practicing));
  document.querySelector('#expand')?.addEventListener('click', () => practice(!practicing));

  document.querySelectorAll('pre code').forEach(block => {
    if (block.id !== 'rag-packet' && !block.closest('.example-output')) window.GuideCode.highlight(block);
  });

  /* In-page search (index.html) */
  let all = [];
  let searchGeneration = 0, modalGeneration = 0;
  const query = document.querySelector('#query');
  const chapter = document.querySelector('#chapter-filter');
  const status = document.querySelector('#status-filter');
  const results = document.querySelector('#results');
  let visibleResults = 20;

  async function search(reset = true) {
    if (reset) visibleResults = 20;
    if (!results) return;
    const generation = ++searchGeneration;
    try { all = await window.GuideSearch.load(chapter.value); }
    catch (error) { document.querySelector('#search-count').textContent = error.message; return; }
    if (generation !== searchGeneration) return;
    const terms = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const filtered = all.filter(q => {
      const text = q.text.toLocaleLowerCase();
      const selected = status.value;
      const stage = window.GuideStudyModel.mastery(state,q.id).stage.toLocaleLowerCase();
      return (!chapter.value || q.slug === chapter.value) && terms.every(term => text.includes(term)) &&
        (selected === 'all' || selected === stage || selected === 'learned' && stage !== 'not started' || selected === 'unlearned' && stage === 'not started' || selected === 'bookmarked' && state.bookmarks[q.id] || selected === 'review' && dueForReview().includes(q.id));
    });
    results.replaceChildren();
    document.querySelector('#search-count').textContent = `${filtered.length} matching question${filtered.length === 1 ? '' : 's'}`;
    if (!filtered.length) {
      const message = document.createElement('p'); message.textContent = 'No questions match these filters. Try fewer words or another chapter.'; results.append(message);
    }
    for (const q of filtered.slice(0, visibleResults)) {
      const link = document.createElement('a'); link.className = 'result'; link.href = new URL(q.href || `${q.slug}.html#q${q.id}`, SITE_ROOT).href;
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
  query?.addEventListener('input', search); chapter?.addEventListener('change', search); status?.addEventListener('change', search);

  document.querySelector('#random')?.addEventListener('click', async () => {
    try { all = await window.GuideSearch.load(); } catch { return; }
    const pending = all.filter(q => !state.learned[q.id]);
    const pool = pending.length ? pending : all;
    const q = pool[Math.floor(Math.random() * pool.length)];
    if (q) {
      const destination = new URL(q.href || `${q.slug}.html#q${q.id}`, SITE_ROOT);
      destination.searchParams.set('mode','practice');
      location.href = destination.href;
    }
  });

  document.querySelector('#term-search')?.addEventListener('input', event => {
    const term = event.target.value.toLocaleLowerCase().trim();
    document.querySelectorAll('[data-term]').forEach(el => { el.hidden = !el.dataset.term.includes(term); });
  });

  /* Modal Search (Spotlight Cmd+K / /) */
  let searchModal = document.querySelector('.search-modal');
  if (!searchModal) {
    searchModal = document.createElement('div');
    searchModal.className = 'search-modal';
    searchModal.setAttribute('role', 'dialog');
    searchModal.setAttribute('aria-modal', 'true');
    searchModal.setAttribute('aria-label', 'Search course topics');
    searchModal.innerHTML = `
      <div class="search-modal-box">
        <div class="search-modal-input">
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8.5" cy="8.5" r="5.5"/><path d="M13 13l4 4"/></svg>
          <input type="search" id="modal-query" aria-label="Search course topics" placeholder="Search topics, tools, and failure modes" autocomplete="off">
          <button type="button" class="search-modal-close" id="modal-close" aria-label="Close modal search">esc</button>
        </div>
        <div class="search-modal-results" id="modal-results"></div>
        <div class="search-modal-footer">
          <span><kbd>↑</kbd><kbd>↓</kbd> to navigate</span>
          <span><kbd>↵</kbd> to select</span>
          <span><kbd>esc</kbd> to close</span>
        </div>
      </div>
    `;
    document.body.appendChild(searchModal);
  }

  const modalQuery = searchModal.querySelector('#modal-query');
  const modalResults = searchModal.querySelector('#modal-results');
  const modalClose = searchModal.querySelector('#modal-close');
  let selectedIndex = -1;

  let searchOpener;
  const inertBefore = new Map();
  function openSearchModal() {
    if (searchModal.classList.contains('is-open')) return;
    searchOpener = document.activeElement;
    for (const child of document.body.children) {
      if (child === searchModal || ['SCRIPT', 'STYLE'].includes(child.tagName)) continue;
      inertBefore.set(child, child.inert);
      child.inert = true;
    }
    searchModal.classList.add('is-open');
    modalQuery.value = '';
    selectedIndex = -1;
    runModalSearch();
    modalQuery.focus();
  }

  function closeSearchModal() {
    searchModal.classList.remove('is-open');
    for (const [child, inert] of inertBefore) child.inert = inert;
    inertBefore.clear();
    searchOpener?.focus();
  }

  async function runModalSearch() {
    const generation = ++modalGeneration;
    let searchData;
    try { searchData = await window.GuideSearch.load(); }
    catch (error) { modalResults.textContent = error.message; return; }
    if (generation !== modalGeneration) return;
    const val = modalQuery.value.toLocaleLowerCase().trim();
    const terms = val.split(/\s+/).filter(Boolean);
    const filtered = terms.length ? searchData.filter(q => {
      const text = q.text.toLocaleLowerCase();
      return terms.every(term => text.includes(term));
    }).slice(0, 15) : searchData.slice(0, 10);

    const focusedResult = modalResults.contains(document.activeElement) ? document.activeElement.href : undefined;
    modalResults.replaceChildren();
    selectedIndex = -1;

    if (!filtered.length) {
      const empty = document.createElement('div');
      empty.className = 'search-modal-empty';
      empty.textContent = 'No matching topics found.';
      modalResults.appendChild(empty);
      if (focusedResult) modalQuery.focus();
      return;
    }

    filtered.forEach((q, i) => {
      const link = document.createElement('a');
      link.className = 'result';
      link.href = new URL(q.href || `${q.slug}.html#q${q.id}`, SITE_ROOT).href;
      link.dataset.index = String(i);

      const title = document.createElement('strong');
      title.textContent = q.title;

      const meta = document.createElement('small');
      meta.textContent = `${q.type || 'Topic'} · ${q.chapter}${state.learned[q.id] ? ' · learned' : ''}${state.bookmarks[q.id] ? ' · bookmarked' : ''}`;

      link.append(meta, title);
      link.addEventListener('click', closeSearchModal);
      modalResults.appendChild(link);
    });
    if (focusedResult) {
      const replacement = [...modalResults.querySelectorAll('a')].find(link => link.href === focusedResult);
      (replacement || modalQuery).focus();
    }
  }

  searchModal.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const controls = [...searchModal.querySelectorAll('input, button, a[href]')];
    const first = controls[0], last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  modalQuery?.addEventListener('input', runModalSearch);
  modalClose?.addEventListener('click', closeSearchModal);
  searchModal.addEventListener('click', (e) => {
    if (e.target === searchModal) closeSearchModal();
  });

  modalQuery?.addEventListener('keydown', (e) => {
    const items = modalResults.querySelectorAll('.result');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = (selectedIndex + 1) % items.length;
      updateSelection(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = (selectedIndex - 1 + items.length) % items.length;
      updateSelection(items);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && items[selectedIndex]) {
        items[selectedIndex].click();
      } else if (items[0]) {
        items[0].click();
      }
    }
  });

  function updateSelection(items) {
    items.forEach((item, idx) => {
      item.classList.toggle('is-selected', idx === selectedIndex);
      if (idx === selectedIndex) item.scrollIntoView({ block: 'nearest' });
    });
  }

  // Intercept all search toolbar links
  document.querySelectorAll('a[href$="#search"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      openSearchModal();
    });
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && searchModal.classList.contains('is-open')) {
      closeSearchModal();
      return;
    }
    if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
      event.preventDefault();
      openSearchModal();
      return;
    }
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !event.target.isContentEditable && !['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
      event.preventDefault();
      openSearchModal();
      return;
    }
  });

  document.querySelector('#distraction-free')?.addEventListener('click', () => {
    focusMode = !focusMode;
    syncControls();
  });

  document.querySelector('#export')?.addEventListener('click', async () => {
    await store.flush();
    const url = URL.createObjectURL(new Blob([JSON.stringify(store.export(), null, 2)], {type:'application/json'}));
    const link = document.createElement('a'); link.href = url; link.download = 'ai-fullstack-study-progress.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  // Filter only the chapter directory: the complete lesson remains available.
  const finder = document.querySelector('.question-finder');
  if (finder) {
    const query = finder.querySelector('#chapter-question-query');
    const kind = finder.querySelector('#chapter-question-kind');
    const items = [...finder.querySelectorAll('[data-finder-text]')];
    finder.querySelector('.finder-controls').hidden = false;
    const filterQuestions = () => {
      const words = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
      let count = 0;
      for (const item of items) {
        item.hidden = !(words.every(word => item.dataset.finderText.includes(word)) &&
          (!kind.value || item.dataset.finderKind === kind.value));
        if (!item.hidden) count++;
      }
      finder.querySelector('#chapter-question-count').textContent = `${count} of ${items.length} questions`;
      finder.querySelector('#chapter-question-empty').hidden = count !== 0;
    };
    query.addEventListener('input', filterQuestions);
    kind.addEventListener('change', filterQuestions);
    finder.querySelector('#chapter-question-reset').addEventListener('click', () => {
      query.value = ''; kind.value = ''; filterQuestions(); query.focus();
    });
  }
  window.GuideAppReady = true;
  window.dispatchEvent(new Event('guide:ready'));
  document.querySelector('#import')?.addEventListener('change', async event => {
    const file = event.target.files[0]; if (!file) return;
    const message = document.querySelector('#storage-status');
    try {
      if (file.size > 20000000) throw new Error('File is too large (20 MB maximum).');
      await store.import(JSON.parse(await file.text()));
      state = store.snapshot; syncControls(); search();
      message.textContent = store.status.warning || 'Progress imported and merged with this browser.';
    } catch (error) { message.textContent = `Import failed: ${error.message}`; }
    event.target.value = '';
  });
})();
