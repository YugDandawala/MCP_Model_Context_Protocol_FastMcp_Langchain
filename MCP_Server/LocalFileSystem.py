import os
import psutil
import platform
from fastmcp import FastMCP

mcp = FastMCP("Local-Project-System")

# Define the ONLY path the AI is allowed to see
FIXED_PATH = "/home/nt020/Downloads/MCP"

@mcp.tool()
def list_directory() -> list:
    """Lists files in the fixed project directory."""
    if not os.path.exists(FIXED_PATH):
        return [f"Error: Path {FIXED_PATH} does not exist."]
    return os.listdir(FIXED_PATH)

@mcp.tool()
def read_project_file(filename: str) -> dict:
    """
    Reads a file from the fixed project directory and returns its content core concepts and absolute path.
    Example: filename='agent.py'
    """
    # Force the path to be inside our FIXED_PATH
    file_path = os.path.join(FIXED_PATH, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return {
            "absolute_path": file_path,
            "content": content
        }
    return {"error": f"File '{filename}' not found in {FIXED_PATH}"}

if __name__ == "__main__":
    mcp.run(transport="stdio")