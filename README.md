# 🛒 shopWithLlama

An AI-powered electronics web app — featuring a conversational shopping assistant that understands natural language queries and orchestrates tool calls to search products, filter by category, and guide users through checkout.

---

## Tech Stack

### Database
**SQLite** (local) 
Raw SQL with a normalized 2-table schema (`categories`, `products`) seeded with ~2,000 real Amazon India electronics listings including live image URLs.

### Backend
**Python + FastAPI**  
REST API with endpoints for product listing (pagination, search, category filtering), individual product detail, and category browsing. CORS-enabled for local frontend development.

### AI Agent
**LangGraph + LangChain + Groq (`llama-3.3-70b-versatile`)**  
A stateful agentic graph that takes natural language user input, selects and calls the appropriate tools (search, filter, fetch product detail), and streams back structured responses. The agent is the core showcase of the project — tool orchestration over raw LLM output.

### Frontend
**React + Vite**  
Component-based UI with a product grid, category/search controls, pagination, product detail view, and an embedded chat widget for interacting with the AI agent.


### Deployment Plan
| Layer | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Railway |
| Database | Supabase (Postgres) |

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com/)

---

### 1. Clone the repo

```bash
git clone https://github.com/your-username/shopping-agent.git
cd shopping-agent
```

---

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
GROQ_API_KEY=your_groq_api_key
```

Seed the database:

```bash
python seed.py
```

Start the backend server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

---

### 3. Set up the frontend

```bash
cd ../frontend
npm install
```

Create a `.env` file inside `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

---
