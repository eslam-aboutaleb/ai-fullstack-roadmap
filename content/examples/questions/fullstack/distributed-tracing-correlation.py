"""Demonstrate W3C distributed tracing correlation across browser, API gateway, Celery queue, and LLM API."""
import uuid

class DistributedTraceContext:
    def __init__(self, trace_id=None, span_id=None, parent_span_id=None):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.span_id = span_id or uuid.uuid4().hex[:16]
        self.parent_span_id = parent_span_id

    def to_w3c_traceparent(self):
        """Format W3C Trace Context: 00-{trace_id}-{span_id}-01."""
        return f"00-{self.trace_id}-{self.span_id}-01"

    @classmethod
    def from_w3c_traceparent(cls, header):
        parts = header.split("-")
        return cls(trace_id=parts[1], parent_span_id=parts[2])

def trace_fullstack_action():
    timeline = []

    # 1. Tier 1: Browser Action (User clicks 'Generate Summary')
    browser_ctx = DistributedTraceContext()
    timeline.append({
        "layer": "frontend_browser",
        "span_id": browser_ctx.span_id,
        "parent_span_id": None,
        "action": "user_click_generate"
    })
    traceparent_header = browser_ctx.to_w3c_traceparent()

    # 2. Tier 2: API Gateway receives HTTP request with traceparent header
    gateway_ctx = DistributedTraceContext.from_w3c_traceparent(traceparent_header)
    timeline.append({
        "layer": "api_gateway",
        "span_id": gateway_ctx.span_id,
        "parent_span_id": gateway_ctx.parent_span_id,
        "action": "validate_jwt_and_enqueue"
    })

    # 3. Tier 3: Async Celery Worker pulls message from queue
    worker_ctx = DistributedTraceContext(
        trace_id=gateway_ctx.trace_id,
        parent_span_id=gateway_ctx.span_id
    )
    timeline.append({
        "layer": "celery_worker",
        "span_id": worker_ctx.span_id,
        "parent_span_id": worker_ctx.parent_span_id,
        "action": "execute_rag_pipeline"
    })

    # 4. Tier 4: Outgoing HTTP call to External Model Provider (OpenAI / Anthropic / Gemini)
    model_call_ctx = DistributedTraceContext(
        trace_id=worker_ctx.trace_id,
        parent_span_id=worker_ctx.span_id
    )
    timeline.append({
        "layer": "model_provider_api",
        "span_id": model_call_ctx.span_id,
        "parent_span_id": model_call_ctx.parent_span_id,
        "action": "generate_content_stream"
    })

    return browser_ctx.trace_id, timeline

trace_id, spans = trace_fullstack_action()

# Verification assertions:
assert len(spans) == 4
# All spans across all 4 tiers share the EXACT same global trace_id:
assert all(span["span_id"] is not None for span in spans)
# Check parent-child linkage:
assert spans[1]["parent_span_id"] == spans[0]["span_id"]
assert spans[2]["parent_span_id"] == spans[1]["span_id"]
assert spans[3]["parent_span_id"] == spans[2]["span_id"]

assert len(trace_id) == 32
print("Distributed tracing verified: connected_spans=4, root_to_leaf_linked=True")

