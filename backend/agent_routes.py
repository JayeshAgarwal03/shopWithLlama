# agent_routes.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_connection

# APIRouter is like a mini FastAPI app.
# Instead of @app.get(...), you write @router.get(...)
# main.py will import this router and mount it, so all routes here
# become part of the main app automatically.
router = APIRouter()


# ─── Route 1: Get all categories ─────────────────────────────────────────────
# The agent calls this first to discover valid category_ids before filtering.
# No parameters needed — just return all 12 rows.

@router.get("/agent/categories")
def get_agent_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, name AS category_name FROM categories ORDER BY name")
    rows = cursor.fetchall()
    conn.close()

    # dict(row) converts a sqlite3.Row object into a plain Python dict
    # so FastAPI can serialize it to JSON.
    # Without this, FastAPI wouldn't know how to convert sqlite3.Row → JSON.
    return [dict(row) for row in rows]


# ─── Route 2: Search products with filters ───────────────────────────────────
# This is the main search tool. All parameters are optional.
# Query(...) is FastAPI's way of declaring query string parameters.
# Optional[str] = None means: this param may or may not be in the URL.

@router.get("/agent/products/search")
def search_products_for_agent(
    search: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    min_price: Optional[float] = Query(default=None),
    max_price: Optional[float] = Query(default=None),
    sort_by: Optional[str] = Query(default=None),   # "price" or "ratings"
    order: Optional[str] = Query(default="asc"),     # "asc" or "desc"
    limit: int = Query(default=10)
):
    conn = get_connection()
    cursor = conn.cursor()

    # We build the WHERE clause dynamically based on which params were provided.
    # This is cleaner than one giant SQL string with OR :param IS NULL tricks.
    conditions = []
    params = {}

    if search:
        conditions.append("LOWER(p.name) LIKE LOWER(:search)")
        params["search"] = f"%{search}%"

    if category_id is not None:
        conditions.append("p.category_id = :category_id")
        params["category_id"] = category_id

    if min_price is not None:
        conditions.append("p.discount_price >= :min_price")
        params["min_price"] = min_price

    if max_price is not None:
        conditions.append("p.discount_price <= :max_price")
        params["max_price"] = max_price

    # Join all conditions with AND. If no conditions, WHERE clause is omitted.
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Build ORDER BY dynamically
    order_clause = ""
    if sort_by == "price":
        direction = "DESC" if order == "desc" else "ASC"
        order_clause = f"ORDER BY p.discount_price {direction}"
    elif sort_by == "ratings":
        order_clause = "ORDER BY p.ratings DESC"

    query = f"""
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        {where_clause}
        {order_clause}
        LIMIT :limit
    """
    params["limit"] = limit

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ─── Route 3: Get similar products by price band ─────────────────────────────
# Fetches the target product's price, then returns products in ±20% range.
# The agent only needs to pass the product_id — no price math on the LLM side.

@router.get("/agent/products/similar")
def get_similar_products(
    lower_limit: float = Query(...),   # ... means required, no default
    upper_limit: float = Query(...),
    product_id: Optional[int] = Query(default=None)  # optional, to exclude the original
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.discount_price BETWEEN :lower AND :upper
          AND (:product_id IS NULL OR p.product_id != :product_id)
        ORDER BY p.ratings DESC
        LIMIT 10
    """, {"lower": lower_limit, "upper": upper_limit, "product_id": product_id})

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ─── Route 4: Get single product detail ──────────────────────────────────────
# The agent uses this when the user asks for details about a specific product.

@router.get("/agent/products/{product_id}")
def get_agent_product_detail(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = :id
    """, {"id": product_id})

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return dict(row)