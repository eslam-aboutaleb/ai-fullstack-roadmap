"""Implement multi-tier conversation memory with recursive sliding window compaction and entity ledgers."""

class ConversationMemoryManager:
    def __init__(self, recent_window_size=2):
        self.recent_window_size = recent_window_size
        self.entity_ledger = {}     # Structured state: entity_id -> value
        self.archived_summary = ""   # Compressed bulleted summary of older turns
        self.active_turns = []       # Verbatim recent turns

    def record_turn(self, role, content, extracted_entities=None):
        if extracted_entities:
            self.entity_ledger.update(extracted_entities)
            
        self.active_turns.append({"role": role, "content": content})
        
        # When active turns exceed window size, compact oldest turns into summary:
        if len(self.active_turns) > self.recent_window_size:
            self._compact_oldest_turns()

    def _compact_oldest_turns(self):
        # Pop oldest turn to compress
        oldest = self.active_turns.pop(0)
        summary_line = f"- {oldest['role'].upper()}: {oldest['content'][:60]}..."
        if self.archived_summary:
            self.archived_summary += "\n" + summary_line
        else:
            self.archived_summary = summary_line

    def build_prompt_context(self):
        """Assemble the complete prompt memory package."""
        lines = []
        if self.entity_ledger:
            lines.append("### Active Verified Entity State:")
            for k, v in self.entity_ledger.items():
                lines.append(f"  * {k}: {v}")
                
        if self.archived_summary:
            lines.append("### Conversation History Summary:")
            lines.append(self.archived_summary)
            
        lines.append("### Recent Conversation Turns:")
        for t in self.active_turns:
            lines.append(f"{t['role'].capitalize()}: {t['content']}")
            
        return "\n".join(lines)

memory = ConversationMemoryManager(recent_window_size=2)

# Turn 1: User specifies billing account and requested limit
memory.record_turn(
    "user", "Please update the monthly budget limit for account acc_9981 to $5,000.",
    extracted_entities={"account_id": "acc_9981", "budget_limit": "$5,000"}
)

# Turn 2: Assistant confirms
memory.record_turn("assistant", "I have staged the budget update for account acc_9981 to $5,000. Do you confirm?")

# Turn 3: User approves (triggers compaction of Turn 1)
memory.record_turn("user", "Yes, I confirm this change.")

# Turn 4: Assistant executes (triggers compaction of Turn 2)
memory.record_turn("assistant", "Budget successfully updated and committed.")

prompt_text = memory.build_prompt_context()

# Verify that entity ledger preserved account_id and budget_limit even after Turn 1 was compacted:
assert "account_id: acc_9981" in prompt_text
assert "budget_limit: $5,000" in prompt_text
assert "Conversation History Summary:" in prompt_text
# Verify that only the last 2 turns remain in active verbatim turns:
assert len(memory.active_turns) == 2

print(f"Conversation compaction verified: active_turns={len(memory.active_turns)}, entities={list(memory.entity_ledger.keys())}")
