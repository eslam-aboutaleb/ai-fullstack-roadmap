from mcp.server.fastmcp import FastMCP
mcp = FastMCP("public-help-demo")

@mcp.tool()
def search_public_help(query: str) -> dict:
    """Search synthetic public help articles; performs no writes."""
    if not 1 <= len(query.strip()) <= 500:
        return {"status": "invalid_input", "items": []}
    return {"status": "ok", "items": [{"id": "demo-1", "text": "Office hours: 9–5"}]}

if __name__ == "__main__":
    mcp.run(transport="stdio")
# Pin a compatible v1 SDK. Remote auth, quotas, and deployment are separate work.
