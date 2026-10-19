/* Browser-only interactions; core content remains readable without JavaScript. */
(() => {
  'use strict';
  const KEY = 'ai-fullstack-roadmap-v1';
  const QUESTION_COUNT = Number(document.body.dataset.questionCount) || 0;
  const THEMES = ['light', 'warm', 'dark'];
  let state = { learned: {}, bookmarks: {}, notes: {}, theme: 'light' };
  let storageOK = true;

  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || localStorage.getItem('ragnor-learning-v1') || 'null');
    if (saved && typeof saved === 'object') state = validate(saved);
  } catch { storageOK = false; }

  function validate(input) {
    const out = {
      learned: {},
      bookmarks: {},
      notes: {},
      theme: THEMES.includes(input.theme) ? input.theme : 'light'
    };
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
    const themeBtn = document.querySelector('#theme');
    if (themeBtn) {
      const labels = { light: 'Theme: Light ☀️', warm: 'Theme: Warm ☕', dark: 'Theme: Dark 🌙' };
      themeBtn.textContent = labels[state.theme] || 'Change theme';
      themeBtn.title = 'Switch reading theme (Light → Warm Sepia → Dark)';
    }

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
    const idx = THEMES.indexOf(state.theme);
    state.theme = THEMES[(idx + 1) % THEMES.length];
    document.documentElement.dataset.theme = state.theme;
    save();
    syncControls();
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

  /* Syntax Highlighting */
  function highlightCode() {
    const kwRegex = /\b(def|class|return|if|elif|else|for|while|try|except|finally|with|as|import|from|in|is|not|and|or|lambda|yield|raise|assert|async|await|pass|break|continue|None|True|False|SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|JOIN|LEFT|INNER|GROUP|BY|ORDER|LIMIT|HAVING|CREATE|TABLE|ALTER|DROP|PRIMARY|KEY|FOREIGN|REFERENCES|function|const|let|var)\b/g;
    const builtinRegex = /\b(int|str|float|bool|list|dict|set|tuple|print|len|range|enumerate|zip|map|filter|sorted|isinstance|type|super|self|cls|open|VARCHAR|INTEGER|TEXT|TIMESTAMP|BOOLEAN|BIGINT|UUID)\b/g;

    function esc(s) {
      return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    document.querySelectorAll('pre code').forEach(block => {
      if (block.id === 'rag-packet' || block.dataset.highlighted) return;
      block.dataset.highlighted = 'true';
      let raw = block.textContent;
      const tokens = [];
      const replacer = (cls, m) => {
        const id = tokens.length;
        tokens.push(`<span class="${cls}">${esc(m)}</span>`);
        return `@@@TOK${id}@@@`;
      };

      raw = raw.replace(/(#.*$|--.*$|\/\/.*$)/gm, m => replacer('tok-cmt', m));
      raw = raw.replace(/("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')/g, m => replacer('tok-str', m));
      raw = raw.replace(/(@[a-zA-Z_]\w*)/g, m => replacer('tok-deco', m));
      raw = raw.replace(/\b(\d+(?:\.\d+)?)\b/g, m => replacer('tok-num', m));
      raw = raw.replace(kwRegex, m => replacer('tok-kw', m));
      raw = raw.replace(builtinRegex, m => replacer('tok-builtin', m));

      let res = esc(raw);
      tokens.forEach((t, i) => {
        res = res.replace(`@@@TOK${i}@@@`, t);
      });
      block.innerHTML = res;
    });
  }
  highlightCode();

  /* In-page search (index.html) */
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
          <input type="search" id="modal-query" placeholder="Type to search all 703 topics, tools, failure modes..." autocomplete="off">
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

  function openSearchModal() {
    searchModal.classList.add('is-open');
    modalQuery.value = '';
    selectedIndex = -1;
    runModalSearch();
    setTimeout(() => modalQuery.focus(), 50);
  }

  function closeSearchModal() {
    searchModal.classList.remove('is-open');
  }

  function runModalSearch() {
    const searchData = window.GUIDE_SEARCH || [];
    const val = modalQuery.value.toLocaleLowerCase().trim();
    const terms = val.split(/\s+/).filter(Boolean);
    const filtered = terms.length ? searchData.filter(q => {
      const text = q.text.toLocaleLowerCase();
      return terms.every(term => text.includes(term));
    }).slice(0, 15) : searchData.slice(0, 10);

    modalResults.replaceChildren();
    selectedIndex = -1;

    if (!filtered.length) {
      const empty = document.createElement('div');
      empty.className = 'search-modal-empty';
      empty.textContent = 'No matching topics found.';
      modalResults.appendChild(empty);
      return;
    }

    filtered.forEach((q, i) => {
      const link = document.createElement('a');
      link.className = 'result';
      link.href = `${q.slug}.html#q${q.id}`;
      link.dataset.index = String(i);

      const title = document.createElement('strong');
      title.textContent = q.title;

      const meta = document.createElement('small');
      meta.textContent = `${q.type || 'Topic'} · ${q.chapter}${state.learned[q.id] ? ' · learned' : ''}${state.bookmarks[q.id] ? ' · bookmarked' : ''}`;

      link.append(meta, title);
      link.addEventListener('click', closeSearchModal);
      modalResults.appendChild(link);
    });
  }

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
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
      event.preventDefault();
      openSearchModal();
    }
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
      state = { theme: incoming.theme, learned: { ...state.learned, ...incoming.learned }, bookmarks: { ...state.bookmarks, ...incoming.bookmarks }, notes: { ...state.notes, ...incoming.notes } };
      save(); syncControls(); search(); message.textContent = storageOK ? 'Progress imported and merged with this browser.' : 'Imported for this session. Browser storage is unavailable; keep your export.';
    } catch (err) { message.textContent = `Import failed: ${err.message}`; }
    event.target.value = '';
  });
  window.addEventListener('storage', event => {
    if (event.key !== KEY || !event.newValue) return;
    try { state = validate(JSON.parse(event.newValue)); syncControls(); search(); } catch { /* Ignore external changes. */ }
  });
})();
