from mcp.server.fastmcp import FastMCP
mcp = FastMCP('synthetic-policy')
@mcp.tool()
def synthetic_excerpt(document_id: str) -> str:
    if document_id != 'D1':
        raise ValueError('unknown synthetic document')
    return 'Exchange only'
if __name__ == '__main__':
    mcp.run(transport='stdio')
