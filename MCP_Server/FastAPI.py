from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastmcp import FastMCP

# Create FastAPI app (same as main.py)
app = FastAPI(title="FastAPI")
templates = Jinja2Templates(directory="templates")

@app.get("/file", response_class=HTMLResponse)
async def serve_fastmcp_demo(request: Request):
    """Serve FastAPI to FastMCP demo page"""
    return templates.TemplateResponse("index.html", {"request": request})

# 🔥 MAGIC: Convert FastAPI endpoints to MCP tools automatically
mcp = FastMCP.from_fastapi(app=app, name="FastAPI")

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
