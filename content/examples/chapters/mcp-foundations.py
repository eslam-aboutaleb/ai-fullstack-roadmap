tool_schema = {
    "name": "search_public_help",
    "description": "Search synthetic public help articles; no writes.",
    "inputSchema": {
        "type": "object",
        "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 500}},
        "required": ["query"], "additionalProperties": False,
    },
}
assert tool_schema["inputSchema"]["additionalProperties"] is False
# Negotiate protocol capabilities through a compatible SDK, not this object alone.
