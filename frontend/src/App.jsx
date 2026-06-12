// src/App.jsx

import { useState, useEffect } from "react";
import { getProducts, getCategories } from "./api.js";
//import ProductCard from "./components/ProductCard.jsx";
import ProductGrid from "./components/ProductGrid.jsx";
import Controls from "./components/Controls.jsx";
import Pagination from "./components/Pagination.jsx";
import ProductDetail from "./components/ProductDetail.jsx";
import "./App.css";

const PAGE_SIZE = 12;

function App() {

  // ── Data coming FROM the API ──────────────────────────────────────
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState([]);

  // ── Loading / error state ─────────────────────────────────────────
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ── Filter inputs — these trigger re-fetches when they change ─────
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);

  // ── What user is currently typing (not yet committed) ────────────
  const [searchDraft, setSearchDraft] = useState("");

  // ── Which product detail view to show (null = show grid) ─────────
  // null means "no product selected, show the listing"
  // a number means "show detail view for this product ID"
  const [selectedId, setSelectedId] = useState(null);


  // ── Effect 1: fetch categories once on mount ──────────────────────
  // Empty array [] means this runs exactly once — when App first loads.
  // Categories don't change, so we never need to re-fetch them.
  useEffect(function() {

    getCategories()
      .then(function(data) {
        setCategories(data);
      })
      .catch(function(err) {
        console.error("Could not load categories:", err);
      });

  }, []);


  // ── Effect 2: fetch products when search / category / page change ─
  // React watches these three variables. Any time one changes,
  // this whole effect re-runs from the top.
  useEffect(function() {

    setLoading(true);
    setError(null);

    getProducts(page, search, category)
      .then(function(data) {
        setProducts(data.products);
        setTotal(data.total);
        setLoading(false);
      })
      .catch(function(err) {
        setError(err.message);
        setLoading(false);
      });

  }, [search, category, page]);


  // ── Handler: user commits a search ───────────────────────────────
  // Called when user presses Enter or clicks Search button.
  // Resets page to 1 — otherwise you'd be on page 8 of new results.
  function handleSearchCommit() {
    setPage(1);
    setSearch(searchDraft);
  }

  // ── Handler: category dropdown changes ───────────────────────────
  function handleCategoryChange(newCategory) {
    setPage(1);
    setCategory(newCategory);
  }

  // ── Handler: user clicks a product card ──────────────────────────
  function handleCardClick(id) {
    setSelectedId(id);
  }

  // ── Handler: user clicks Back in detail view ─────────────────────
  function handleBack() {
    setSelectedId(null);
  }

  // ── Pagination math ───────────────────────────────────────────────
  // Math.ceil(1982 / 12) = 166 total pages
  const totalPages = Math.ceil(total / PAGE_SIZE);


  // ── Render ────────────────────────────────────────────────────────
  // JSX note: you can only return ONE root element.
  // The outer <div className="app"> is that single root.
  return (
    <div className="app">

      {/* Detail overlay — only shown when a card is clicked.
          In JSX, { } lets you drop back into JavaScript.
          This is a ternary: condition ? ifTrue : ifFalse       */}
      {selectedId !== null ? (
        <ProductDetail
          id={selectedId}
          onBack={handleBack}
        />
      ) : null}

      {/* Header */}
      <header className="site-header">
        <div className="header-inner">
          <div className="logo">
            
            <span className="logo-text">Shopping Agent</span>
          </div>
          <p className="header-tagline">1,982 Amazon India electronics</p>
        </div>
      </header>


      {/* Chat placeholder — Phase 5 will replace this with the LangGraph agent */}
      <div className="chat-placeholder">
        <span className="chat-placeholder-icon">💬</span>
          <p className="chat-placeholder-text">AI Shopping Agent</p>
          <p className="chat-placeholder-sub">Coming in Phase 5 · LangGraph + Groq</p>
      </div>

      {/* Search bar + category dropdown */}
      <Controls
        searchDraft={searchDraft}
        onSearchDraftChange={setSearchDraft}
        onSearchCommit={handleSearchCommit}
        categories={categories}
        selectedCategory={category}
        onCategoryChange={handleCategoryChange}
      />

      {/* Results count line */}
      <div className="results-bar">
        <div className="results-inner">
          {loading === false && error === null && (
            <p className="results-count">
              {total} products found
              {search !== "" ? " for \"" + search + "\"" : ""}
              {category !== "" ? " in " + category : ""}
            </p>
          )}
        </div>
      </div>

      {/* Product grid — passes down loading/error/products/handler */}
      <main className="main-content">
        <ProductGrid
          products={products}
          loading={loading}
          error={error}
          onCardClick={handleCardClick}
        />
      </main>

      {/* Pagination — only shown when there are multiple pages */}
      {totalPages > 1 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}

      <footer className="site-footer">
        <p>Portfolio project · FastAPI + React · Amazon India electronics dataset</p>
      </footer>

    </div>
  );
}

export default App;