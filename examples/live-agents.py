class LiveState:
    def __init__(self): self.revision = 0
    def new_input(self):
        self.revision += 1
        return self.revision
    def can_publish(self, based_on): return based_on == self.revision
state = LiveState()
first = state.new_input()
state.new_input()  # User corrects the task while work is running.
assert not state.can_publish(first)
# Use conditional writes for cross-process authoritative state changes.
