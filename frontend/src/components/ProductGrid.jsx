// src/components/ProductGrid.jsx

import ProductCard from "./ProductCard.jsx";

function ProductGrid({ products, loading, error, onCardClick }) {

  // ── State 1: loading ───────────────────────────────────────────
  if (loading === true) {
    return (
      <div className="state-screen">
        <div className="spinner"></div>
        <p>Loading products...</p>
      </div>
    );
  }

  // ── State 2: error ─────────────────────────────────────────────
  if (error !== null) {
    return (
      <div className="state-screen error">
        <p>Something went wrong: {error}</p>
        <p className="hint">Is your FastAPI server running at localhost:8000?</p>
      </div>
    );
  }

  // ── State 3: empty results ─────────────────────────────────────
  if (products.length === 0) {
    return (
      <div className="state-screen">
        <p>No products found. Try a different search.</p>
      </div>
    );
  }

  // ── State 4: the actual grid ───────────────────────────────────
  // products.map() turns each product object into a ProductCard component.
  // key={product.id} lets React track each card individually.
  // onCardClick is passed down so each card can report clicks back to App.
  return (
    <div className="product-grid">
      {products.map(function(product) {
        return (
          <ProductCard
            key={product.id}
            product={product}
            onCardClick={onCardClick}
          />
        );
      })}
    </div>
  );
}

export default ProductGrid;