# backend/main.py

from dotenv import load_dotenv
load_dotenv()  # must be first — before any agent/langchain imports

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import httpx

from database import get_connection
from models import Product, Category, PaginatedProducts
from agent_routes import router as agent_router
from agents.shopping_agent import ShoppingAgent
from langchain_core.messages import HumanMessage, AIMessage


# ─── Request/Response models ──────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str


# ─── Agent singleton ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Shopping Agent...")
    app.state.agent = ShoppingAgent()
    print("Agent ready.")
    yield
    print("Shutting down.")


# ─── App initialization — one definition, everything included ─────────────────

app = FastAPI(title="Shopping Agent APIs", lifespan=lifespan)

app.include_router(agent_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── /chat ────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    # chat_request — your Pydantic model (message + history)
    # request — FastAPI's Request object, which has .app.state

    lc_history = []
    for msg in chat_request.history:
        if msg.role == "user":
            lc_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_history.append(AIMessage(content=msg.content))

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: request.app.state.agent.run(chat_request.message, lc_history)
    )

    return ChatResponse(response=response)


# ─── /categories ─────────────────────────────────────────────────────────────

@app.get("/categories", response_model=list[Category])
def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ─── /products ───────────────────────────────────────────────────────────────

@app.get("/products", response_model=PaginatedProducts)
def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str]   = Query(None),
    page: int               = Query(1, ge=1),
    page_size: int          = Query(20, ge=1, le=100),
):
    conn = get_connection()

    filters = []
    params  = []

    if category:
        filters.append("LOWER(c.name) LIKE LOWER(?)")
        params.append(f"%{category}%")

    if search:
        filters.append("LOWER(p.name) LIKE LOWER(?)")
        params.append(f"%{search}%")

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    base_query = f"""
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        {where}
    """

    total = conn.execute(
        f"SELECT COUNT(*) FROM ({base_query})", params
    ).fetchone()[0]

    offset = (page - 1) * page_size
    rows = conn.execute(
        f"{base_query} LIMIT ? OFFSET ?",
        params + [page_size, offset]
    ).fetchall()

    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "products": [dict(row) for row in rows],
    }


# ─── /products/{id} ──────────────────────────────────────────────────────────

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = ?
        """,
        (product_id,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    return dict(row)


# ─── /image-proxy ─────────────────────────────────────────────────────────────

@app.get("/image-proxy")
async def image_proxy(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "image/jpeg")
    )