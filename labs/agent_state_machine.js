// Local fixture, not an LLM or production permission system. Node.js or browser console.
(() => {
  function assert(condition, message) { if (!condition) throw new Error(message); }
  function makeAgent({tools, allowedTools, maxSteps = 5, failToolAt = null}) {
    let state = 'idle', step = 0;
    const trajectory = [];
    let terminal;
    function stepThrough(input) {
      if (terminal) return terminal; // Terminal states cannot perform further effects.
      state = 'thinking';
      if (++step > maxSteps) return terminal = {state: state = 'failed', error: 'Max steps exceeded', trajectory};
      const tool = tools.find(item => item.appliesTo(input));
      if (!tool) return terminal = {state: state = 'done', answer: 'No applicable tool.', trajectory};
      if (!allowedTools.includes(tool.name)) return terminal = {state: state = 'failed', error: 'Tool denied', trajectory};
      state = 'acting';
      try {
        if (step === failToolAt) throw new Error('Tool timeout');
        const result = tool.execute(input);
        trajectory.push({step, tool: tool.name, result});
        if (result.final) return terminal = {state: state = 'done', answer: result.text, trajectory};
        return {state: state = 'observing', observation: result.text, trajectory};
      } catch (error) {
        trajectory.push({step, tool: tool.name, error: error.message});
        return {state: state = 'thinking', observation: `Tool failed: ${error.message}`, trajectory};
      }
    }
    return {stepThrough};
  }
  let calls = 0;
  const tools = [{name: 'retrieve', appliesTo: () => true, execute: () => { calls++; return {text: 'Sale items: exchange within 14 days.', final: true}; }}];
  const normal = makeAgent({tools, allowedTools: ['retrieve']});
  assert(normal.stepThrough('policy').state === 'done', 'Successful tool reaches done');
  assert(normal.stepThrough('policy').answer.includes('exchange'), 'Answer is returned');
  assert(calls === 1, 'Repeated calls after done perform no effects');
  const denied = makeAgent({tools, allowedTools: []});
  assert(denied.stepThrough('policy').error === 'Tool denied' && calls === 1, 'Policy checked before execution');
  const retry = makeAgent({tools, allowedTools: ['retrieve'], failToolAt: 1});
  assert(retry.stepThrough('policy').state === 'thinking', 'Transient failure allows bounded retry');
  assert(retry.stepThrough('policy').state === 'done', 'Second attempt recovers');
  const failing = [{name: 'fail', appliesTo: () => true, execute: () => { throw new Error('unavailable'); }}];
  const bounded = makeAgent({tools: failing, allowedTools: ['fail'], maxSteps: 1});
  bounded.stepThrough('policy');
  assert(bounded.stepThrough('policy').error === 'Max steps exceeded', 'Retry budget is enforced');
  console.log('Agent assertions passed: answer, recovery, denial, terminal effects, and retry budget.');
})();
