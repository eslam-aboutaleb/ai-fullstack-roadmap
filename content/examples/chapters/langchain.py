from langchain.agents import create_agent
from langchain.tools import tool

def build_agent(model):
    @tool
    def public_hours(query: str) -> str:
        """Return synthetic public office hours."""
        return "Demo office hours: 9–5"
    return create_agent(model=model, tools=[public_hours],
        system_prompt="Use evidence; disclose missing information.")
