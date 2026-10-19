const operation = {key: 'synthetic-op1', body: {item_id: 'I1'}};
const firstAttempt = {headers: {'Idempotency-Key': operation.key}, body: operation.body};
const retryAttempt = {headers: {'Idempotency-Key': operation.key}, body: operation.body};
console.log(firstAttempt.headers['Idempotency-Key'] === retryAttempt.headers['Idempotency-Key']);
