// src/api.js

const BASE_URL = "http://127.0.0.1:8000";

// ------------------------------------------------------------------
// getProducts
// Fetches one page of products with optional search/category filters.
// Returns: { products: [...], total: 1982, page: 1, page_size: 12 }
// ------------------------------------------------------------------
export async function getProducts(page, search, category) {

  // URLSearchParams builds the query string safely.
  // Handles encoding — spaces become %20, etc.
  const params = new URLSearchParams();
  params.append("page", page);
  params.append("page_size", 12);

  // Only add these if they have a value
  if (search !== "") {
    params.append("search", search);
  }
  if (category !== "") {
    params.append("category", category);
  }

  // Template literal — like Java's String.format but with backticks
  // Final URL example: http://127.0.0.1:8000/products?page=1&page_size=12&search=phone
  const url = `${BASE_URL}/products?${params}`;

  const response = await fetch(url);

  // fetch() does NOT throw on 404 or 500 — you must check manually
  if (response.ok === false) {
    throw new Error("Failed to fetch products");
  }

  // .json() reads the response body and parses it into a JS object
  const data = await response.json();
  return data;
}

// ------------------------------------------------------------------
// getProductById
// Fetches a single product by its ID.
// Returns: { id, name, price, rating, image_url, ... }
// ------------------------------------------------------------------
export async function getProductById(id) {
  const url = `${BASE_URL}/products/${id}`;

  const response = await fetch(url);

  if (response.ok === false) {
    throw new Error("Product not found: " + id);
  }

  const data = await response.json();
  return data;
}

// ------------------------------------------------------------------
// getCategories
// Fetches all 12 categories.
// Returns: [ { id: 1, name: "Smartphones" }, ... ]
// ------------------------------------------------------------------
export async function getCategories() {
  const url = `${BASE_URL}/categories`;

  const response = await fetch(url);

  if (response.ok === false) {
    throw new Error("Failed to fetch categories");
  }

  const data = await response.json();
  return data;
}