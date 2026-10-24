"""Demonstrate Vertical Slice Architecture: validating end-to-end contracts across frontend, API gateway, and worker."""
import json
import uuid

# 1. Tier 1: Frontend Client Contract
# Constructs typed request with client-generated correlation ID:
def frontend_submit_task(prompt, user_id="usr_alice", tenant_id="tenant_acme"):
    client_request_id = f"req_{uuid.uuid4().hex[:12]}"
    payload = {
        "client_request_id": client_request_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "prompt": prompt,
        "parameters": {"temperature": 0.2, "max_tokens": 512}
    }
    return payload

# 2. Tier 2: API Gateway (FastAPI / ASGI)
# Validates schema, enforces auth boundaries, and enqueues task without blocking HTTP thread:
class APIGatewaySlice:
    def __init__(self, message_broker):
        self.broker = message_broker

    def handle_task_submission(self, request_payload, auth_tenant):
        # Validate tenant isolation:
        if request_payload["tenant_id"] != auth_tenant:
            return 403, {"error": "Tenant boundary violation"}
            
        # Validate prompt constraints:
        if not request_payload.get("prompt") or len(request_payload["prompt"]) < 5:
            return 422, {"error": "Prompt must be at least 5 characters"}

        # Enqueue work to asynchronous message queue:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        envelope = {
            "task_id": task_id,
            "client_request_id": request_payload["client_request_id"],
            "tenant_id": auth_tenant,
            "prompt": request_payload["prompt"],
            "status": "queued"
        }
        self.broker.enqueue(envelope)
        
        # Immediate 202 Accepted response with task polling endpoint:
        return 202, {"task_id": task_id, "status": "queued", "check_url": f"/api/tasks/{task_id}"}

# 3. Tier 3: Asynchronous AI Worker (Celery / Background Process)
# Pulls envelope from broker, processes RAG inference, and commits final status:
class BackgroundAIWorkerSlice:
    def __init__(self, message_broker, database_state):
        self.broker = message_broker
        self.db = database_state

    def process_next_task(self):
        envelope = self.broker.dequeue()
        if not envelope: return None

        # Execute simulated inference:
        generated_answer = f"Synthesized evidence for: {envelope['prompt']}"
        
        # Commit durable result tagged with client correlation ID:
        self.db[envelope["task_id"]] = {
            "task_id": envelope["task_id"],
            "client_request_id": envelope["client_request_id"],
            "tenant_id": envelope["tenant_id"],
            "status": "completed",
            "result": generated_answer
        }
        return envelope["task_id"]

# End-to-End Slice Execution:
class MockBroker:
    def __init__(self): self.queue = []
    def enqueue(self, item): self.queue.append(item)
    def dequeue(self): return self.queue.pop(0) if self.queue else None

broker = MockBroker()
durable_db = {}
gateway = APIGatewaySlice(broker)
worker = BackgroundAIWorkerSlice(broker, durable_db)

# Step 1: Frontend sends request
client_req = frontend_submit_task("Analyze Q3 infrastructure expenses.")

# Step 2: Gateway accepts
code, res = gateway.handle_task_submission(client_req, auth_tenant="tenant_acme")
assert code == 202
assigned_task_id = res["task_id"]

# Step 3: Worker processes
processed_id = worker.process_next_task()
assert processed_id == assigned_task_id

# Step 4: Verification of end-to-end data contract across all 3 tiers:
final_record = durable_db[assigned_task_id]
assert final_record["client_request_id"] == client_req["client_request_id"]
assert final_record["tenant_id"] == "tenant_acme"
assert final_record["status"] == "completed"

print(f"Vertical slice contract verified: task_id={assigned_task_id}, client_id={final_record['client_request_id']}, status={final_record['status']}")

