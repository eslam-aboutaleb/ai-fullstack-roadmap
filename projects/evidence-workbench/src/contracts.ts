export type Frame =
  | {requestId: string; seq: number; type: 'delta'; text: string}
  | {requestId: string; seq: number; type: 'done'; citations: string[]; abstain: boolean};

export function parseFrame(value: unknown): Frame {
  if (typeof value !== 'object' || value === null) throw new Error('Frame must be an object');
  const row = value as Record<string, unknown>;
  if (typeof row.requestId !== 'string' || !Number.isSafeInteger(row.seq) || Number(row.seq) < 1) throw new Error('Invalid identity or sequence');
  if (row.type === 'delta' && typeof row.text === 'string' && row.text.length <= 2000) {
    return {requestId: row.requestId, seq: Number(row.seq), type: 'delta', text: row.text};
  }
  if (row.type === 'done' && Array.isArray(row.citations) && row.citations.length <= 10 && new Set(row.citations).size === row.citations.length &&
      row.citations.every((id: unknown) => typeof id === 'string' && /^[ab]-policy@1$/.test(id)) && typeof row.abstain === 'boolean') {
    return {requestId: row.requestId, seq: Number(row.seq), type: 'done', citations: row.citations, abstain: row.abstain};
  }
  throw new Error('Invalid frame contract');
}

export async function* frames(body: ReadableStream<Uint8Array>): AsyncGenerator<Frame> {
  const reader = body.getReader();
  const decoder = new TextDecoder('utf-8', {fatal: true});
  let pending = '';
  function parse(line: string) { return parseFrame(JSON.parse(line) as unknown); }
  try {
    while (true) {
      const chunk = await reader.read();
      pending += decoder.decode(chunk.value, {stream: !chunk.done});
      let end: number;
      while ((end = pending.indexOf('\n')) >= 0) {
        if (end > 16384) throw new Error('Frame limit exceeded');
        const line = pending.slice(0, end); pending = pending.slice(end + 1);
        if (line) yield parse(line);
      }
      if (pending.length > 16384) throw new Error('Frame limit exceeded');
      if (chunk.done) break;
    }
    if (pending.trim()) throw new Error('Truncated frame');
  } finally { await reader.cancel().catch(() => undefined); reader.releaseLock(); }
}
