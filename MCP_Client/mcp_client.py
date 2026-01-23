from langchain_mcp_adapters.client import MultiServerMCPClient

# Pointing to the SSE endpoint of your server
client = MultiServerMCPClient({
    "expense_tracker": {
        "transport": "http",
        "url": "http://127.0.0.1:8000/mcp",
    },
    "LocalFileSystem": {
        "transport": "stdio",
        "command": "/home/nt020/.local/bin/uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "/home/nt020/Downloads/MCP/MCP_Server/LocalFileSystem.py"
       ]
    },
})

async def get_tools():
    """Fetch and return tools from the MCP server."""
    tools = await client.get_tools()
    return tools

__all__ = ["client", "get_expense_tools"]

# from langchain_mcp_adapters.client import MultiServerMCPClient
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # Connect to OFFICIAL GitHub MCP server
# client = MultiServerMCPClient({
#     "github": {
#         "transport": "http",
#         "url": "https://api.githubcopilot.com/mcp",
#         "headers": {
#             "Authorization": f"{os.getenv('GITHUB_TOKEN')}"
#         }
#     }
# })

# async def get_github_tools():
#     """Get GitHub MCP tools (create_file, list_files, create_issue, etc.)"""
#     tools = await client.get_tools()
#     print(f"✅ Loaded {len(tools)} GitHub MCP tools:")
#     for tool in tools:
#         print(f"{tool.name}")
#     return tools

# # Export for agent use
# __all__ = ["client", "get_github_tools"]