def apply_event(state, event):
    if event["seq"] <= state["seq"]: return state
    if event["seq"] != state["seq"] + 1: raise ValueError("resume from snapshot")
    return {"seq": event["seq"], "text": state["text"] + event.get("delta", "")}
s = {"seq": 0, "text": ""}
s = apply_event(s, {"seq": 1, "delta": "Hi"})
assert apply_event(s, {"seq": 1, "delta": "Hi"}) == s
