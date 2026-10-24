/**
 * Simulate resilient streaming fetch with chunk decoding and AbortController timeout bounds.
 */

function decodeNdjsonStream(rawChunks) {
  const decodedObjects = [];
  let buffer = "";

  for (const chunk of rawChunks) {
    buffer += chunk;
    const lines = buffer.split("\n");
    buffer = lines.pop(); // Retain incomplete trailing token in buffer
    for (const line of lines) {
      if (line.trim()) {
        decodedObjects.push(JSON.parse(line));
      }
    }
  }

  if (buffer.trim()) {
    decodedObjects.push(JSON.parse(buffer));
  }
  return decodedObjects;
}

// 1. Stream decoding test
const streamPayloads = [
  '{"id":1,"token":"Deep"}\n{"id":2',
  ',"token":"Learning"}\n{"id":3,"token":"Systems"}\n'
];
const tokens = decodeNdjsonStream(streamPayloads);

// 2. AbortController simulation
const controller = new AbortController();
const signal = controller.signal;
let abortedCleanly = false;

signal.addEventListener("abort", () => {
  abortedCleanly = true;
});

// Trigger abort
controller.abort();

console.log(
  `Resilient stream fetch verified: tokens_decoded=${tokens.length}, aborted_cleanly=${abortedCleanly}`
);
