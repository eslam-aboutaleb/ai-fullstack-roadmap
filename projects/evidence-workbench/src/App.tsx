import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { frames } from './contracts';

type State = {phase: 'idle' | 'loading' | 'complete' | 'failed' | 'cancelled'; text: string; citations: string[]; message: string};
const idle: State = {phase: 'idle', text: '', citations: [], message: 'Ready. Ask about the sale policy.'};
type Owner = 'a' | 'b';

function Answer({state}: {state: State}) {
  return <section aria-labelledby="answer-heading"><h2 id="answer-heading">Evidence and answer</h2>
    <p role="status" aria-live="polite">{state.message}</p>
    <pre id="answer">{state.text}</pre>
    <ul aria-label="Cited source identities">{state.citations.map(id => <li key={id}>{id}</li>)}</ul>
  </section>;
}

export default function App() {
  const [owner, setOwner] = useState<Owner>('a');
  const [query, setQuery] = useState('What is the sale policy?');
  const [scenario, setScenario] = useState('normal');
  const [state, setState] = useState<State>(idle);
  const generation = useRef(0);
  const active = useRef<AbortController | null>(null);
  // Only external-resource cleanup belongs in this Effect; submission is an event.
  useEffect(() => () => { generation.current++; active.current?.abort(); }, []);

  function invalidate() { generation.current++; active.current?.abort(); active.current = null; }
  function changeOwner(value: Owner) { invalidate(); setOwner(value); setState(idle); }
  function cancel() {
    invalidate(); setState(previous => ({...previous, phase: 'cancelled', citations: [], message: 'Cancelled locally. No remote action was requested.'}));
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); invalidate();
    const mine = generation.current;
    const requestId = crypto.randomUUID();
    const controller = new AbortController(); active.current = controller;
    const deadline = window.setTimeout(() => controller.abort(new DOMException('Request deadline exceeded', 'TimeoutError')), 10000);
    setState({phase: 'loading', text: '', citations: [], message: 'Reading evidence…'});
    let text = '', last = 0, terminal = false;
    const seen = new Map<number, string>();
    try {
      const response = await fetch('/api/answer', {method: 'POST', signal: controller.signal,
        headers: {'Content-Type': 'application/json', 'Authorization': `Bearer demo-${owner}`},
        body: JSON.stringify({query, requestId, scenario})});
      if (!response.ok || !response.body) throw new Error(`Request failed (${response.status})`);
      if (!response.headers.get('content-type')?.startsWith('application/x-ndjson')) throw new Error('Unexpected stream format');
      for await (const frame of frames(response.body)) {
        if (generation.current !== mine) return;
        if (frame.requestId !== requestId) throw new Error('Response identity mismatch');
        const encoded = JSON.stringify(frame);
        if (seen.has(frame.seq)) {
          if (seen.get(frame.seq) !== encoded) throw new Error('Conflicting replay');
          continue;
        }
        if (terminal || frame.seq !== last + 1 || seen.size >= 128) throw new Error('Invalid stream transition');
        seen.set(frame.seq, encoded); last = frame.seq;
        if (frame.type === 'delta') {
          text += frame.text;
          if (text.length > 8000) throw new Error('Answer limit exceeded');
          setState({phase: 'loading', text, citations: [], message: 'Reading evidence…'});
        } else {
          if (frame.citations.some(id => id !== `${owner}-policy@1`) || frame.abstain !== (frame.citations.length === 0)) throw new Error('Evidence scope violation');
          terminal = true;
          setState({phase: 'complete', text, citations: frame.citations, message: frame.abstain ? 'Complete: no supported answer.' : 'Complete: evidence received.'});
        }
      }
      if (!terminal) throw new Error('Connection closed before completion');
    } catch (error: unknown) {
      if (generation.current === mine) setState({phase: 'failed', text, citations: [], message: `Failed: ${error instanceof Error ? error.message : 'Unknown error'}`});
    } finally { window.clearTimeout(deadline); if (generation.current === mine) active.current = null; }
  }
  return <main><p className="eyebrow">LOCAL ENGINEERING PROJECT</p><h1>Evidence workbench</h1>
    <p>A real browser/API boundary with synthetic documents. The two demo identities are public fixtures.</p>
    <form onSubmit={submit}>
      <label htmlFor="owner">Demo identity</label><select id="owner" value={owner} onChange={e => changeOwner(e.currentTarget.value as Owner)}>
        <option value="a">Owner A</option><option value="b">Owner B</option></select>
      <label htmlFor="query">Question</label><textarea id="query" value={query} onChange={e => setQuery(e.currentTarget.value)} required maxLength={500}/>
      <label htmlFor="scenario">Failure fixture</label><select id="scenario" value={scenario} onChange={e => setScenario(e.currentTarget.value)}>
        <option value="normal">Normal</option><option value="slow">Slow response</option><option value="disconnect">Missing completion</option><option value="malformed">Malformed event</option></select>
      <div className="actions"><button type="submit">{state.phase === 'loading' ? 'Restart question' : 'Ask question'}</button>
        <button type="button" onClick={cancel} disabled={state.phase !== 'loading'}>Cancel</button></div>
    </form><Answer state={state}/>
  </main>;
}
