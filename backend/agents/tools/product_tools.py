# backend/agents/tools/product_tools.py

import httpx
from typing import Optional
from langchain_core.tools import tool
from agents.tools.config import BACKEND_URL


@tool(parse_docstring=True)
def search_products(
    search: str = "",
    category_id: int = 0,
    min_price: float = 0,
    max_price: float = 0,
    sort_by: str = "",
    order: str = "asc"
) -> str:
    """Search for products using filters. All parameters are optional.
    Call get_categories first if you need a category_id.
    Use this for queries like: 'show me laptops under 50000',
    'best rated earphones', 'cheap USB cables'.

    Args:
        search: Keyword to search in product names. E.g. 'wireless mouse'. Use empty string if not needed.
        category_id: Integer ID of the category. Get from get_categories first. Use 0 if not needed.
        min_price: Minimum price in Indian Rupees. Use 0 if no lower bound.
        max_price: Maximum price in Indian Rupees. Use 0 if no upper bound.
        sort_by: Sort results by 'price' or 'ratings'. Use empty string for default order.
        order: Sort direction 'asc' or 'desc'. Only used when sort_by is set.
    """
    params = {}
    if search:
        params["search"] = search
    if category_id:
        params["category_id"] = category_id
    if min_price:
        params["min_price"] = min_price
    if max_price:
        params["max_price"] = max_price
    if sort_by:
        params["sort_by"] = sort_by
    if order:
        params["order"] = order

    response = httpx.get(f"{BACKEND_URL}/agent/products/search", params=params)
    products = response.json()

    # Slim down — LLM only gets what it needs to form a response
    slim = [
        {
            "product_id": p["product_id"],
            "name": p["name"],
            "discount_price": p["discount_price"],
            "ratings": p["ratings"],
            "category_name": p["category_name"]
        }
        for p in products
    ]

    return str(slim)


@tool(parse_docstring=True)
def get_similar_products(product_id: int, current_price: float) -> str:
    """Find products similar in price to a given product.
    Use this when the user says 'show me similar products' or
    'what else is in this price range' while viewing a product.

    Args:
        product_id: The integer ID of the reference product to exclude from results.
        current_price: The price of the reference product in Indian Rupees.
                       The tool will search within 80 to 120 percent of this price.
    """
    lower_limit = current_price * 0.8
    upper_limit = current_price * 1.2

    params = {
        "lower_limit": lower_limit,
        "upper_limit": upper_limit,
        "product_id": product_id
    }

    response = httpx.get(f"{BACKEND_URL}/agent/products/similar", params=params)
    return response.text


@tool(parse_docstring=True)
def get_product_detail(product_id: int) -> str:
    """Get full details of a single product by its ID.
    Use this when the user asks for more information about a specific product,
    or when you need the price of a product before calling get_similar_products.

    Args:
        product_id: The integer ID of the product to fetch details for.
    """
    response = httpx.get(f"{BACKEND_URL}/agent/products/{product_id}")
    return response.text