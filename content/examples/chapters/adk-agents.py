from google.adk.agents import LlmAgent

def build_agent(model):
    def search_demo(query: str) -> dict:
        """Search synthetic public help text; performs no writes."""
        return {"status": "ok", "items": ["Demo office hours: 9–5"]}
    return LlmAgent(
        name="support_demo", model=model,
        instruction="Use tools for facts. If evidence is missing, say so.",
        tools=[search_demo],
    )
# Host supplies a compatible model, session service, runner, and trusted identity.
