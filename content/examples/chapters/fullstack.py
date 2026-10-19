def reduce_status(state, event):
    transitions = {
        ("waiting", "started"): "streaming",
        ("streaming", "persisted_result"): "complete",
        ("streaming", "error"): "incomplete",
    }
    return transitions.get((state, event), state)
assert reduce_status("streaming", "text_delta") != "complete"
