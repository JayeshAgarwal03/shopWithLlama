# backend/agents/tools/category_tools.py

import httpx
from langchain_core.tools import tool
from agents.tools.config import BACKEND_URL


@tool(parse_docstring=True)
def get_categories() -> str:
    """Get all available product categories in the store.
    Use this tool first when the user mentions a category by name
    (e.g. 'headphones', 'laptops') so you can find the correct category_id
    before calling search_products.

    """
    response = httpx.get(f"{BACKEND_URL}/agent/categories")
    return response.text