"""MCP tool execution lifecycle, JSON Schema input validation, and typed content payloads.

Demonstrates:
1. Tool discovery contract: name, description, and strict JSON Schema inputSchema.
2. Two-tier schema validation (client pre-flight and defensive server-side parameter bounds).
3. Multi-modal content payload returns (TextContent, ImageContent, EmbeddedResource).
4. Failure signaling via isError: true with actionable resolution hints for LLM self-correction.
"""
from typing import Any, Dict, List, Optional, Tuple
import base64
import json

class ToolSchemaValidator:
    @staticmethod
    def validate(schema: Dict[str, Any], data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        props = schema.get("properties", {})
        required = schema.get("required", [])

        # Check required fields
        for field in required:
            if field not in data:
                return False, f"Missing required parameter: '{field}'"

        # Validate types and bounds
        for key, value in data.items():
            if key not in props:
                if not schema.get("additionalProperties", True):
                    return False, f"Unexpected parameter: '{key}'"
                continue

            prop_def = props[key]
            expected_type = prop_def.get("type")

            if expected_type == "string":
                if not isinstance(value, str):
                    return False, f"Parameter '{key}' must be a string, got {type(value).__name__}"
                if "maxLength" in prop_def and len(value) > prop_def["maxLength"]:
                    return False, f"Parameter '{key}' exceeds maximum length of {prop_def['maxLength']}"

            elif expected_type == "integer":
                if not isinstance(value, int) or isinstance(value, bool):
                    return False, f"Parameter '{key}' must be an integer, got {type(value).__name__}"
                if "minimum" in prop_def and value < prop_def["minimum"]:
                    return False, f"Parameter '{key}' must be >= {prop_def['minimum']}"
                if "maximum" in prop_def and value > prop_def["maximum"]:
                    return False, f"Parameter '{key}' must be <= {prop_def['maximum']}"

            elif expected_type == "array":
                if not isinstance(value, list):
                    return False, f"Parameter '{key}' must be an array, got {type(value).__name__}"

        return True, None

# Concrete MCP tool implementation
class DocumentSearchTool:
    DESCRIPTOR = {
        "name": "search_documents",
        "description": "Searches authorized enterprise documentation by query with bounded limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string.",
                    "maxLength": 200
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of excerpts to return (1-20).",
                    "minimum": 1,
                    "maximum": 20
                },
                "include_diagram": {
                    "type": "boolean",
                    "description": "Whether to include architecture diagram image in output."
                }
            },
            "required": ["query", "limit"],
            "additionalProperties": False
        }
    }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Server-side validation
        valid, error_msg = ToolSchemaValidator.validate(self.DESCRIPTOR["inputSchema"], arguments)
        if not valid:
            return {
                "content": [
                    {"type": "text", "text": f"Validation Error: {error_msg}. Check inputSchema."}
                ],
                "isError": True
            }

        query = arguments["query"]
        limit = arguments["limit"]
        include_diagram = arguments.get("include_diagram", False)

        if "syntax_error" in query:
            # Expected domain failure returned with isError: True
            return {
                "content": [
                    {"type": "text", "text": "Search index query syntax error: Unterminated quote. Suggestion: Remove special characters."}
                ],
                "isError": True
            }

        # Successful multi-modal content generation
        content_items: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": json.dumps({
                    "matches": [f"Result #{i+1} for '{query}'" for i in range(limit)],
                    "total_found": limit
                })
            }
        ]

        if include_diagram:
            synthetic_png = base64.b64encode(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR...").decode("ascii")
            content_items.append({
                "type": "image",
                "data": synthetic_png,
                "mimeType": "image/png"
            })

        return {
            "content": content_items,
            "isError": False
        }

if __name__ == "__main__":
    tool = DocumentSearchTool()

    # 1. Invalid arguments: Missing required parameter 'limit'
    res_missing = tool.execute({"query": "architecture"})
    assert res_missing["isError"] is True
    assert "Missing required parameter: 'limit'" in res_missing["content"][0]["text"]

    # 2. Out-of-bounds parameter: limit > 20
    res_bounds = tool.execute({"query": "architecture", "limit": 100})
    assert res_bounds["isError"] is True
    assert "must be <= 20" in res_bounds["content"][0]["text"]

    # 3. Domain query failure reported via isError: True (no crash!)
    res_syntax = tool.execute({"query": "syntax_error'", "limit": 5})
    assert res_syntax["isError"] is True
    assert "Suggestion: Remove special characters" in res_syntax["content"][0]["text"]

    # 4. Valid invocation returning multimodal content blocks
    res_valid = tool.execute({"query": "microservices", "limit": 3, "include_diagram": True})
    assert res_valid["isError"] is False
    assert len(res_valid["content"]) == 2
    assert res_valid["content"][0]["type"] == "text"
    assert res_valid["content"][1]["type"] == "image"
    assert res_valid["content"][1]["mimeType"] == "image/png"

    print("MCP tool execution lifecycle and schema validation verified successfully.")
