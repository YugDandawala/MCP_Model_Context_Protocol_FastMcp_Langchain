import os
from fastmcp import FastMCP, Context

mcp = FastMCP("LocalFileSystem")

# Define the ONLY path the AI is allowed to see
FIXED_PATH = "/home/nt020/Downloads/MCP"


@mcp.tool()
def list_directory() -> list:
    """Lists files in the fixed project directory."""
    if not os.path.exists(FIXED_PATH):
        return [f"Error: Path {FIXED_PATH} does not exist."]
    return os.listdir(FIXED_PATH)


@mcp.tool()
async def read_project_file(filename: str, ctx: Context) -> dict:
    """
    Reads a file from the fixed project directory.
    If extension is missing, asks the user for it.
    Then asks the client LLM to summarize the file.
    """

    # ---------- ELICITATION ----------
    if "." not in filename:
        extension = await ctx.elicit(
            message=f"You entered '{filename}'. What is the file extension? (e.g. py, txt, json)",
            input_type="text"
        )
        filename = f"{filename}.{extension.strip()}"

    # Force the path to be inside FIXED_PATH
    file_path = os.path.join(FIXED_PATH, filename)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return {"error": f"File '{filename}' not found in {FIXED_PATH}"}

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # ---------- SAMPLING ----------
    analysis = await ctx.sample(
        f"""
        Analyze this file and explain clearly:
        1. What this file does
        2. Important functions or logic
        3. Any potential issues

        File content:
        ----------------
        {content[:6000]}
        ----------------
        """,
        system_prompt="You are a senior software engineer doing code understanding.",
        temperature=0.1,
        max_tokens=400
    )

    return {
        "absolute_path": file_path,
        "content": content,
        "ai_summary": analysis.text
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
