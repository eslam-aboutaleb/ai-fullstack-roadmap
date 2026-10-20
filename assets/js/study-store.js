/* IndexedDB event journal. Each mutation is an independent record, not a full-state overwrite. */
(() => {
  'use strict';
  const model = window.GuideStudyModel;
  const DATABASE = 'ai-fullstack-study', PREFIX = 'ai-study-event-v3:', RESET_ID = '__study-reset__';
  const LEGACY_KEYS = ['ragnor-learning-v1', 'ai-fullstack-roadmap-v1'];
  const store = new EventTarget();
  let events = [], database, clock = 0, pending = Promise.resolve(), channel;
  let backend = 'memory', warning = '';
  const uuid = () => crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  function update(incoming, notify = true) {
    events = model.compact(model.merge(events, incoming.map(record => record.kind === 'reset' ? {...record,id:RESET_ID} : record)));
    for (const event of incoming) clock = Math.max(clock, event.time || 0);
    if (notify) store.dispatchEvent(new Event('change'));
  }
  function transaction(records) {
    return new Promise((resolve, reject) => {
      const tx = database.transaction('events', 'readwrite'), table = tx.objectStore('events');
      const gate = table.get(RESET_ID);
      gate.onsuccess = () => {
        const resets = records.filter(record => record.kind === 'reset').map(record => ({...record,id:RESET_ID}));
        const barrier = model.merge(gate.result ? [gate.result] : [], resets).at(-1);
        if (barrier) {
          if (!gate.result || barrier.time > gate.result.time) table.clear();
          table.put(barrier); update([barrier], false);
        }
        for (const record of records) {
          if (record.kind === 'reset' || barrier && record.time <= barrier.time) continue;
          const request = table.get(record.id);
          request.onsuccess = () => {
            const canonical = model.merge(request.result ? [request.result] : [], [record])[0];
            table.put(canonical); update([canonical], false);
          };
        }
      };
      tx.oncomplete = resolve; tx.onerror = () => reject(tx.error); tx.onabort = () => reject(tx.error);
    });
  }
  function localWrite(records) {
    try {
      if (!records.length) { localStorage.setItem('ai-study-storage-probe', '1'); localStorage.removeItem('ai-study-storage-probe'); }
      let previous;
      try { previous = JSON.parse(localStorage.getItem(PREFIX+RESET_ID) || 'null'); } catch { /* recover below */ }
      const resets = records.filter(record => record.kind === 'reset').map(record => ({...record,id:RESET_ID}));
      const barrier = model.merge(previous && model.eventValid(previous) ? [previous] : [], resets).at(-1);
      if (barrier && (!previous || barrier.time > previous.time)) {
        const keys = [];
        for (let index=0;index<localStorage.length;index++) keys.push(localStorage.key(index));
        for (const key of keys) if (key?.startsWith(PREFIX) || LEGACY_KEYS.includes(key) || key==='ai-roadmap-reading-v1') localStorage.removeItem(key);
      }
      if (barrier) { localStorage.setItem(PREFIX+RESET_ID, JSON.stringify(barrier)); update([barrier], false); }
      for (const record of records) if (record.kind !== 'reset' && (!barrier || record.time > barrier.time)) {
        let saved;
        try { saved = JSON.parse(localStorage.getItem(PREFIX + record.id) || 'null'); } catch { /* Replace a corrupt copy. */ }
        const canonical = model.merge(saved ? [saved] : [], [record])[0];
        localStorage.setItem(PREFIX + record.id, JSON.stringify(canonical));
        update([canonical], false);
      }
      backend = 'localStorage'; return true;
    } catch {
      warning = 'Browser storage is unavailable or full. Export a backup; new changes may last only for this session. To erase inaccessible data, use browser site-data controls.';
      return false;
    }
  }
  async function persist(records) {
    if (database) {
      try { await transaction(records); backend = 'IndexedDB'; }
      catch { localWrite(records); warning ||= 'IndexedDB is unavailable. A localStorage fallback is being used; export a backup.'; }
    } else localWrite(records);
    if (records.some(record => record.kind === 'reset') && backend === 'IndexedDB') { const cleared = localWrite(records); backend = 'IndexedDB'; if (cleared) warning = ''; }
    try { channel?.postMessage(model.compact(records)); } catch { /* Memory-only mode remains usable. */ }
    store.dispatchEvent(new Event('change'));
  }
  function appendRecords(records) {
    if (!records.every(model.eventValid)) throw new Error('Invalid study record');
    update(records);
    pending = pending.then(() => persist(records));
    return pending;
  }
  function append(record) { return appendRecords([record]); }
  function mutation(kind, data) {
    return {id: uuid(), time: clock = Math.max(Date.now(), clock + 1), kind, ...data};
  }
  function openDatabase() {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) { reject(new Error('IndexedDB unavailable')); return; }
      const request = indexedDB.open(DATABASE, 3);
      let expired = false;
      const timeout = setTimeout(() => { expired = true; reject(new Error('IndexedDB did not open in time')); }, 2000);
      request.onupgradeneeded = () => {
        if (!request.result.objectStoreNames.contains('events')) request.result.createObjectStore('events', {keyPath:'id'});
      };
      request.onsuccess = () => {
        clearTimeout(timeout);
        if (expired) { request.result.close(); return; }
        resolve(request.result);
      };
      request.onerror = () => { clearTimeout(timeout); reject(request.error); };
      request.onblocked = () => { expired = true; clearTimeout(timeout); reject(new Error('Another tab blocks the storage upgrade')); };
    });
  }
  store.ready = (async () => {
    const migration = [];
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!key?.startsWith(PREFIX)) continue;
        try { const record = JSON.parse(localStorage.getItem(key)); if (model.eventValid(record)) migration.push(record); }
        catch { warning = 'An unreadable journal record was skipped. Export your remaining study record.'; }
      }
      // Current key wins migration conflicts; existing v3 events are newer than time 0.
      const legacy = {};
      for (const key of LEGACY_KEYS) {
        try {
          const input = JSON.parse(localStorage.getItem(key) || 'null');
          if (input && typeof input === 'object' && !Array.isArray(input)) {
            for (const [field, value] of Object.entries(input)) legacy[field] = value && typeof value === 'object' && !Array.isArray(value) ? {...legacy[field], ...value} : value;
          }
        } catch { warning = 'An old study record is damaged; valid records were recovered. Keep an export before clearing site data.'; }
      }
      migration.push(...model.legacy(legacy));
    } catch { /* IndexedDB may still work when localStorage is blocked. */ }
    update(migration, false);
    try {
      database = await openDatabase();
      database.onversionchange = () => { database.close(); database = undefined; warning = 'Storage changed in another tab. Reload after exporting.'; };
      const saved = await new Promise((resolve, reject) => {
        const request = database.transaction('events').objectStore('events').getAll();
        request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error);
      });
      update(saved.filter(model.eventValid), false);
      await transaction(migration); backend = 'IndexedDB';
    } catch {
      database?.close(); database = undefined;
      localWrite(events);
    }
    try { channel = new BroadcastChannel(DATABASE); channel.onmessage = event => { if (Array.isArray(event.data)) update(event.data); }; } catch { /* storage events provide fallback notifications. */ }
    store.dispatchEvent(new Event('change'));
  })();
  Object.defineProperties(store, {
    snapshot: {get: () => model.reduce(events)},
    status: {get: () => ({backend, warning})}
  });
  store.set = (field, topic, value) => append(mutation('set', {field, topic: String(topic), value}));
  store.recordAttempt = value => {
    const records = [mutation('attempt', {value})];
    if (value.passed !== null && value.kind !== 'self-review') {
      records.push(mutation('set', {field:'reviews', topic:String(value.topic), value:model.schedule(store.snapshot.reviews[value.topic], value.passed, Date.now())}));
    }
    // Attempt evidence and its next review commit in the same IDB transaction.
    return appendRecords(records);
  };
  store.review = (topic, passed = true) => {
    const now = Date.now();
    return store.set('reviews', topic, model.schedule(store.snapshot.reviews[topic], passed, now));
  };
  store.clear = () => append({...mutation('reset', {}),id:RESET_ID});
  store.flush = () => pending;
  store.export = () => ({version: 3, exportedAt: new Date().toISOString(), events: model.compact(events)});
  store.import = async input => {
    let incoming;
    if (input?.version === 3 && Array.isArray(input.events) && input.events.length <= 50000 && input.events.every(model.eventValid)) incoming = input.events;
    else if (input?.version === 1 && input.learned && !Array.isArray(input.learned) && input.notes && !Array.isArray(input.notes) && typeof input.learned === 'object' && typeof input.notes === 'object') {
      incoming = model.legacy(input, uuid()).map(e => ({...e, time: clock = Math.max(Date.now(), clock + 1)}));
    } else throw new Error('Choose a valid version 1 or version 3 study export.');
    incoming = incoming.map(record => record.kind === 'reset' ? {...record,id:RESET_ID} : record);
    update(incoming); pending = pending.then(() => persist(incoming)); await pending;
  };
  window.addEventListener('storage', event => {
    if (!event.key?.startsWith(PREFIX) || !event.newValue) return;
    try { const record = JSON.parse(event.newValue); if (model.eventValid(record)) update([record]); } catch { /* Preserve existing valid state. */ }
  });
  window.GuideStudy = Object.freeze({store, model});
})();
