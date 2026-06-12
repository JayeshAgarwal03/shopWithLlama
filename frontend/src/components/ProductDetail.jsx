// src/components/ProductDetail.jsx

import { useState, useEffect } from "react";
import { getProductById } from "../api.js";

function ProductDetail({ id, onBack }) {

  // ── Local state — only this component needs this data ──────────
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);


  // ── Fetch the full product when this component mounts ──────────
  // [id] in the dependency array means: if the id prop ever changes,
  // re-run this effect and fetch the new product.
  useEffect(function() {

    // Reset state before each fetch
    // This matters if the user navigates from product 5 to product 12 —
    // we don't want product 5's data showing while product 12 loads
    setLoading(true);
    setError(null);
    setProduct(null);

    getProductById(id)
      .then(function(data) {
        setProduct(data);
        setLoading(false);
      })
      .catch(function(err) {
        setError(err.message);
        setLoading(false);
      });

  }, [id]);


  // ── Format price (same logic as ProductCard) ───────────────────
  let formattedPrice = "Price unavailable";
  if (product !== null && product.discount_price !== null && product.discount_price !== undefined) {
    const formatter = new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    });
    formattedPrice = formatter.format(product.discount_price);
  }

  const API_BASE = "http://127.0.0.1:8000";

    let imageSrc = "https://placehold.co/400x400?text=No+Image";
    if (product !== null && product.image !== null && product.image !== undefined && product.image !== "") {
        imageSrc = API_BASE + "/image-proxy?url=" + encodeURIComponent(product.image);
    }

  // ── Render ─────────────────────────────────────────────────────
  // The overlay covers the whole screen (fixed position in CSS).
  // Clicking Back calls onBack() in App, which sets selectedId to null,
  // which unmounts this component entirely.
  return (
    <div className="detail-overlay">
      <div className="detail-card">

        <button className="back-btn" onClick={onBack}>
          ← Back to products
        </button>

        {/* Loading state */}
        {loading === true && (
          <div className="state-screen">
            <div className="spinner"></div>
            <p>Loading product...</p>
          </div>
        )}

        {/* Error state */}
        {error !== null && loading === false && (
          <div className="state-screen error">
            <p>Could not load product: {error}</p>
          </div>
        )}

        {/* Loaded state — only render when product exists */}
        {product !== null && loading === false && (
          <div className="detail-inner">

            <div className="detail-image-wrap">
              <img
                src={imageSrc}
                alt={product.name}
                onError={function(e) {
                  e.target.src = "https://placehold.co/400x400?text=No+Image";
                }}
              />
            </div>

            <div className="detail-info">

              <span className="detail-category">
                {product.category_name}
              </span>

              <h1 className="detail-name">
                {product.name}
              </h1>

              <p className="detail-price">
                {formattedPrice}
              </p>

              {/* Rating — only show if the product has one */}
              {product.ratings !== null && product.ratings !== undefined && (
                <div className="detail-rating">
                  <span className="rating-value">{product.ratings} / 5</span>
                  {product.num_ratings !== null && (
                    <span className="rating-count">
                      ({product.num_ratings} ratings)
                    </span>
                  )}
                </div>
              )}

              {/* Brand — only show if it exists */}
              {product.brand !== null && product.brand !== undefined && (
                <div className="detail-meta-row">
                  <span className="meta-label">Brand</span>
                  <span className="meta-value">{product.brand}</span>
                </div>
              )}

              {/* This button does nothing yet — Stripe comes in Phase 4 */}
              <button className="buy-btn">
                Add to Cart
              </button>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default ProductDetail;