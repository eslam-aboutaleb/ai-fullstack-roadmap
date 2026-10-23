"""Demonstrate two-phase distributed idempotency: Redis fast claim and PostgreSQL durable record."""
import hashlib
import json

class TwoPhaseIdempotencyEngine:
    def __init__(self):
        # Redis simulated store (fast, volatile in-memory mutex)
        self.redis_store = {}
        # Relational database simulated table (durable ACID table with UNIQUE key constraint)
        self.db_idempotency_table = {}

    def execute_idempotent_operation(self, idempotency_key, request_payload, business_fn):
        payload_hash = hashlib.sha256(json.dumps(request_payload, sort_keys=True).encode()).hexdigest()
        
        # 1. Fast Cache Check (Redis):
        cached = self.redis_store.get(idempotency_key)
        if cached:
            if cached["payload_hash"] != payload_hash:
                raise ValueError("Idempotency key reused with mismatched request payload! (422 Unprocessable)")
            if cached["status"] == "in_flight":
                raise RuntimeError("Concurrent request in progress for this idempotency key! (409 Conflict)")
            return cached["response"]

        # 2. Redis Mutex Acquisition:
        self.redis_store[idempotency_key] = {"status": "in_flight", "payload_hash": payload_hash}

        try:
            # 3. Check Durable DB Ledger:
            if idempotency_key in self.db_idempotency_table:
                record = self.db_idempotency_table[idempotency_key]
                return record["response"]

            # 4. Execute Core Business Transaction:
            response_data = business_fn(request_payload)

            # 5. Persist to Durable DB Ledger inside transaction:
            self.db_idempotency_table[idempotency_key] = {
                "payload_hash": payload_hash,
                "response": response_data,
                "status": "committed"
            }

            # 6. Update Redis cache with committed response:
            self.redis_store[idempotency_key] = {
                "status": "committed",
                "payload_hash": payload_hash,
                "response": response_data
            }
            return response_data
        except Exception:
            # Release in-flight claim if operation crashed before durable commit
            self.redis_store.pop(idempotency_key, None)
            raise

engine = TwoPhaseIdempotencyEngine()
order_payload = {"order_id": "ord_101", "amount": 99.00}

# First call: executes business logic
res1 = engine.execute_idempotent_operation("idemp_key_abc", order_payload, lambda p: {"status": "confirmed", "tx": "tx_555"})

# Second call (retry with same key & payload): returns cached durable result without re-executing logic!
res2 = engine.execute_idempotent_operation("idemp_key_abc", order_payload, lambda p: {"status": "re-executed-error"})

assert res1 == res2 == {"status": "confirmed", "tx": "tx_555"}
print(f"Idempotent two-phase execution verified: result={res2['status']}, durable_records={len(engine.db_idempotency_table)}")
