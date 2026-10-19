from dataclasses import dataclass
@dataclass
class Budget:
    remaining: int
    def reserve(self, units=1):
        if units <= 0: raise ValueError("positive units required")
        if units > self.remaining: raise RuntimeError("budget exhausted")
        self.remaining -= units
budget = Budget(2)
budget.reserve()  # Parent and children share the same object in this local demo.
budget.reserve()
assert budget.remaining == 0
# A fleet requires atomic shared accounting and deadline propagation.
