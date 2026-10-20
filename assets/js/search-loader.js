/* Fetch static search shards only when the learner requests a search. */
(() => {
  'use strict';
  const ROOT = new URL('./', document.currentScript.src), cache = new Map();
  let manifest;
  function read(path) {
    if (!cache.has(path)) cache.set(path, fetch(new URL(path,ROOT)).then(response => {
      if (!response.ok) throw new Error('Search index unavailable. Follow the chapter or question-bank links.');
      return response.json();
    }).catch(error => { cache.delete(path); throw error; }));
    return cache.get(path);
  }
  async function load(chapter = '') {
    manifest ||= read('search/manifest.json');
    let info;
    try { info = await manifest; } catch (error) { manifest = undefined; throw error; }
    const shards=info.shards.filter(shard => !chapter || shard.chapters.includes(chapter));
    const groups=await Promise.all(shards.map(shard => read(shard.url)));
    return groups.flat().filter(row => !chapter || row.slug===chapter);
  }
  window.GuideSearch=Object.freeze({load});
})();
