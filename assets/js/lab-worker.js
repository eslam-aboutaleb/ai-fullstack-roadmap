/* One disposable worker per run. Teaching isolation, not a hardened sandbox. */
'use strict';
self.onmessage = async event => {
  const {code, cases, language, ticket, runtimeURL} = event.data;
  const reply = self.postMessage.bind(self);
  let output = '', capped = false;
  const emit = (...args) => {
    const text = args.map(value => typeof value === 'string' ? value : String(value)).join(' ') + '\n';
    const remaining = Math.max(0, 12000 - output.length);
    output += text.slice(0, remaining);
    if (text.length > remaining) capped = true;
  };
  function equal(a, b) {
    if (typeof a === 'number' && typeof b === 'number') return Number.isFinite(a) && Math.abs(a-b) < 1e-9;
    if (a === b) return true;
    if (!a || !b || typeof a !== 'object' || typeof b !== 'object' || Array.isArray(a) !== Array.isArray(b)) return false;
    const keys = Object.keys(a).sort(), other = Object.keys(b).sort();
    return keys.length === other.length && keys.every((key, i) => key === other[i] && equal(a[key], b[key]));
  }
  try {
    if (typeof code !== 'string' || code.length > 64000 || !Array.isArray(cases) || cases.length > 30) throw new Error('Lab input limit exceeded');
    let solve;
    if (language === 'python') {
      importScripts(new URL('pyodide.js', runtimeURL).href);
      const python = await loadPyodide({indexURL:runtimeURL, stdout:emit, stderr:emit, packages:[]});
      reply({ticket, type:'ready'});
      python.globals.set('submitted_source', code);
      // A declared import allowlist is a teaching constraint, not a security boundary.
      python.runPython(`
import ast, json
allowed_imports = {'math', 'json', 'statistics', 'collections', 'itertools', 'functools'}
tree = ast.parse(submitted_source)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        names = [alias.name.split('.')[0] for alias in node.names]
    elif isinstance(node, ast.ImportFrom):
        names = [(node.module or '').split('.')[0]]
    else:
        continue
    if any(name not in allowed_imports for name in names):
        raise ImportError('This lab allows only: ' + ', '.join(sorted(allowed_imports)))
namespace = {}
exec(compile(tree, '<learner>', 'exec'), namespace)
if not callable(namespace.get('solve')):
    raise ValueError('Define a solve(data) function')
`);
      solve = input => {
        python.globals.set('case_json', JSON.stringify(input));
        return JSON.parse(python.runPython("json.dumps(namespace['solve'](json.loads(case_json)), allow_nan=False)"));
      };
    } else {
      reply({ticket, type:'ready'});
      const blocked = () => { throw new Error('Network access is not part of this local lab'); };
      self.fetch = blocked; self.XMLHttpRequest = blocked; self.WebSocket = blocked; self.importScripts = blocked;
      const console = Object.freeze({log:emit, warn:emit, error:emit, info:emit});
      solve = new Function('console', '"use strict";\n'+code+'\n;return typeof solve === "function" ? solve : undefined;')(console);
      if (typeof solve !== 'function') throw new Error('Define a solve(data) function');
    }
    const results = [];
    for (const test of cases) {
      try {
        const actual = await solve(structuredClone(test.input));
        results.push({name:test.name, passed:equal(actual, test.expected), actual:JSON.stringify(actual)?.slice(0, 1000) || String(actual), expected:JSON.stringify(test.expected).slice(0, 1000)});
      } catch (error) { results.push({name:test.name, passed:false, error:String(error.message).slice(0,1000)}); }
    }
    reply({ticket, type:'result', results, output:output + (capped ? '\n[output truncated at 12,000 characters]' : '')});
  } catch (error) {
    reply({ticket, type:'error', message:String(error.message).slice(0, 2000), output});
  }
};
