import re

DOCUMENTS = [
    {"id": "general:r1", "text": "Standard items may be refunded within 30 days."},
    {"id": "sale:r3", "text": "Sale items can be exchanged within 14 days. Refunds are not offered for sale items."},
    {"id": "shipping:r2", "text": "Delivery takes 3 to 5 days."},
]

def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def retrieve(question):
    query = words(question)
    ranked = sorted(DOCUMENTS,
        key=lambda doc: len(query & words(doc["text"])), reverse=True)
    return [doc for doc in ranked[:1] if query & words(doc["text"])]

def assemble_request(question):
    evidence = retrieve(question)
    if not evidence:
        return {"status": "insufficient_evidence", "question": question}
    return {
        "status": "ready",
        "instructions": "Answer only from the evidence. Preserve exceptions. Cite its ID.",
        "question": question,
        "evidence": evidence,
    }

packet = assemble_request("Can I return a sale item?")
assert packet["evidence"][0]["id"] == "sale:r3"
assert "14 days" in packet["evidence"][0]["text"]
assert assemble_request("ZXQ123")["status"] == "insufficient_evidence"
# Inspect packet: these are the facts an approved generator would receive.
# This tiny lexical baseline has no semantic search, production auth, or live LLM.
