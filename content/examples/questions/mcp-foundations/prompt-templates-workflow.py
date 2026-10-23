"""MCP Prompt templates and complete minimal first MCP server architecture.

Demonstrates:
1. Prompt discovery contract (prompts/list): Advertised prompt templates, descriptions, and argument schemas.
2. Parameterized prompt retrieval (prompts/get): Dynamic interpolation, role-based message generation, and embedded resources.
3. Minimal complete first MCP project structure combining:
   - 1 Tool (procedural computation with side effects)
   - 1 Resource (read-only system configuration)
   - 1 Prompt (standardized, server-curated incident diagnosis workflow)
"""
from typing import Any, Dict, List, Optional
import hashlib
import json

class FirstMcpServer:
    def __init__(self):
        # 1. Exposed Resource
        self._config_resource = {
            "uri": "config://system/runtime.json",
            "name": "System Runtime Configuration",
            "mimeType": "application/json",
            "content": json.dumps({"environment": "production", "max_workers": 8, "log_level": "INFO"})
        }

        # 2. Exposed Tool Descriptor
        self._tool_descriptor = {
            "name": "calculate_hash",
            "description": "Calculates SHA-256 checksum for verification.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "maxLength": 1000}
                },
                "required": ["text"]
            }
        }

        # 3. Exposed Prompt Descriptor
        self._prompt_descriptor = {
            "name": "diagnose_system",
            "description": "Generates a structured system triage review embedding runtime config.",
            "arguments": [
                {
                    "name": "incident_id",
                    "description": "The tracking identifier of the incident.",
                    "required": True
                },
                {
                    "name": "symptom",
                    "description": "Observed system anomaly or error message.",
                    "required": True
                }
            ]
        }

    # Prompt Protocol Handlers
    def list_prompts(self) -> List[Dict[str, Any]]:
        return [self._prompt_descriptor]

    def get_prompt(self, name: str, arguments: Dict[str, str]) -> Dict[str, Any]:
        if name != "diagnose_system":
            raise KeyError(f"Prompt '{name}' not found")

        incident_id = arguments.get("incident_id")
        symptom = arguments.get("symptom")
        if not incident_id or not symptom:
            raise ValueError("Arguments 'incident_id' and 'symptom' are required")

        # Curated multi-turn messages embedding the runtime configuration resource
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Incident Triage Request [ID: {incident_id}]\n"
                        f"Reported Symptom: {symptom}\n\n"
                        f"Please inspect the embedded runtime configuration below and provide:\n"
                        f"1. Potential root causes.\n"
                        f"2. Recommended mitigation steps."
                    )
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "resource",
                    "resource": {
                        "uri": self._config_resource["uri"],
                        "mimeType": self._config_resource["mimeType"],
                        "text": self._config_resource["content"]
                    }
                }
            }
        ]

        return {
            "description": f"Diagnosis workflow for incident {incident_id}",
            "messages": messages
        }

    # Tool Execution Handler
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name != "calculate_hash":
            return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

        text = arguments.get("text", "")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return {
            "content": [{"type": "text", "text": json.dumps({"sha256": digest})}],
            "isError": False
        }

    # Resource Read Handler
    def read_resource(self, uri: str) -> Dict[str, Any]:
        if uri != self._config_resource["uri"]:
            raise KeyError(f"Resource not found: {uri}")
        return {
            "contents": [
                {
                    "uri": self._config_resource["uri"],
                    "mimeType": self._config_resource["mimeType"],
                    "text": self._config_resource["content"]
                }
            ]
        }

if __name__ == "__main__":
    server = FirstMcpServer()

    # 1. Prompt discovery
    prompts = server.list_prompts()
    assert len(prompts) == 1
    assert prompts[0]["name"] == "diagnose_system"
    assert len(prompts[0]["arguments"]) == 2

    # 2. Dynamic prompt compilation with embedded resource
    prompt_result = server.get_prompt("diagnose_system", {
        "incident_id": "INC-8082",
        "symptom": "Elevated p99 latency under traffic spike"
    })
    assert "INC-8082" in prompt_result["description"]
    assert len(prompt_result["messages"]) == 2
    assert "Elevated p99 latency" in prompt_result["messages"][0]["content"]["text"]
    # Verified embedded resource payload
    assert prompt_result["messages"][1]["content"]["type"] == "resource"
    assert "max_workers" in prompt_result["messages"][1]["content"]["resource"]["text"]

    # 3. Tool execution
    tool_res = server.call_tool("calculate_hash", {"text": "hello mcp"})
    assert tool_res["isError"] is False
    assert "f05440e8d8d43423937fa3e9457053ef01c1ac96dc789cd231dd2dc5567ef622" in tool_res["content"][0]["text"]

    # 4. Resource reading
    res_data = server.read_resource("config://system/runtime.json")
    assert "production" in res_data["contents"][0]["text"]

    print("MCP Prompt templates and first server architecture verified successfully.")
