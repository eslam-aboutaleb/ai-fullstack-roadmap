/* Tokenize original text once. DOM text nodes preserve every source character. */
(() => {
  'use strict';
  const tokens = /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)|(#.*$|--.*$|\/\/.*$)|(@[a-zA-Z_]\w*)|(\b\d+(?:\.\d+)?\b)|(\b(?:def|class|return|if|elif|else|for|while|try|except|finally|with|as|import|from|in|is|not|and|or|lambda|yield|raise|assert|async|await|pass|break|continue|None|True|False|SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|JOIN|LEFT|INNER|GROUP|BY|ORDER|LIMIT|HAVING|CREATE|TABLE|ALTER|DROP|PRIMARY|KEY|FOREIGN|REFERENCES|function|const|let|var)\b)|(\b(?:int|str|float|bool|list|dict|set|tuple|print|len|range|enumerate|zip|map|filter|sorted|isinstance|type|super|self|cls|open|VARCHAR|INTEGER|TEXT|TIMESTAMP|BOOLEAN|BIGINT|UUID)\b)/gm;
  const classes = ['tok-str', 'tok-cmt', 'tok-deco', 'tok-num', 'tok-kw', 'tok-builtin'];
  function highlight(block) {
    if (block.dataset.highlighted) return;
    const raw = block.textContent;
    const fragment = document.createDocumentFragment();
    let position = 0;
    for (const match of raw.matchAll(tokens)) {
      fragment.append(document.createTextNode(raw.slice(position, match.index)));
      const span = document.createElement('span');
      span.className = classes[match.slice(1).findIndex(value => value !== undefined)];
      span.textContent = match[0];
      fragment.append(span);
      position = match.index + match[0].length;
    }
    fragment.append(document.createTextNode(raw.slice(position)));
    block.replaceChildren(fragment);
    block.dataset.highlighted = 'true';
  }
  window.GuideCode = Object.freeze({ highlight });
})();
