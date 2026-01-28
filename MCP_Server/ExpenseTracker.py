from fastmcp import FastMCP,Context
import os
import asyncpg
import json
from datetime import datetime

# Connection details
DATABASE_URL = "postgresql://postgres:Admin1234@localhost:5432/langgraph"
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")
_db_pool = None

async def get_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(DATABASE_URL)
        async with _db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    amount FLOAT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
    return _db_pool

def parse_date(date_str):
    """Helper to convert string YYYY-MM-DD to a python date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()

@mcp.tool()
async def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    '''Add a new expense entry (date format: YYYY-MM-DD).'''
    pool = await get_pool()
    # Convert string to date object
    db_date = parse_date(date)
    
    async with pool.acquire() as conn:
        expense_id = await conn.fetchval(
            """
            INSERT INTO expenses(date, amount, category, subcategory, note) 
            VALUES ($1, $2, $3, $4, $5) RETURNING id
            """,
            db_date, amount, category, subcategory, note
        )
        return {"status": "ok", "id": expense_id}

@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    '''List expenses between dates (format: YYYY-MM-DD).'''
    pool = await get_pool()
    # Convert strings to date objects
    d1 = parse_date(start_date)
    d2 = parse_date(end_date)
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN $1 AND $2
            ORDER BY date ASC
            """,
            d1, d2
        )
        # Convert records to dicts and serialize dates back to strings for JSON
        results = []
        for r in rows:
            d = dict(r)
            d['date'] = d['date'].isoformat() # Convert date object back to string "2025-04-15"
            results.append(d)
        return results

@mcp.tool()
async def ai_expense_insights(start_date: str, end_date: str, ctx: Context):  # NEW: Add ctx: Context
    '''AI-powered expense analysis and recommendations'''
    # Get raw data first
    expenses = await list_expenses(start_date, end_date)
    
    # LLM analysis via sampling
    analysis = await ctx.sample(
        f"""
        Analyze these expenses from {start_date} to {end_date}:
        
        {json.dumps(expenses, indent=2)}
        
        Provide:
        1. Spending trends by category
        2. Budget alerts (Food > ₹5000, Travel > ₹10000)
        3. Savings recommendations
        4. Visualization suggestions (bar chart?)
        
        Output in actionable bullet points.
        """,
        system_prompt="You are a personal finance expert. Be specific with amounts and actionable.",
        temperature=0.1,
        max_tokens=600
    )
    
    return {
        "raw_data": expenses,
        "ai_analysis": analysis.text,
        "period": f"{start_date} to {end_date}"
    }

@mcp.tool()
async def summarize(start_date: str, end_date: str, category: str = None):
    '''Summarize expenses (format: YYYY-MM-DD).'''
    pool = await get_pool()
    d1 = parse_date(start_date)
    d2 = parse_date(end_date)
    
    async with pool.acquire() as conn:
        query = "SELECT category, SUM(amount) AS total_amount FROM expenses WHERE date BETWEEN $1 AND $2"
        params = [d1, d2]

        if category:
            query += " AND category = $3"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"
        rows = await conn.fetch(query, *params)
        return [dict(r) for r in rows]

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)