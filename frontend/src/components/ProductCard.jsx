// src/components/ProductCard.jsx

function ProductCard({ product, onCardClick }) {

  // Format price as Indian Rupees
  // Intl.NumberFormat is a browser built-in — no import needed
  let formattedPrice = "Price unavailable";
  if (product.discount_price !== null && product.discount_price !== undefined) {
    const formatter = new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    });
    formattedPrice = formatter.format(product.discount_price);
  }

  // Build a star string from the numeric rating
  // e.g. 4.2 → "★★★★☆"
  let starString = "";
  if (product.ratings !== null && product.ratings !== undefined) {
    const fullStars  = Math.floor(product.ratings);
    const emptyStars = 5 - fullStars;

    let i = 0;
    while (i < fullStars) {
      starString = starString + "★";
      i = i + 1;
    }
    i = 0;
    while (i < emptyStars) {
      starString = starString + "☆";
      i = i + 1;
    }
  }

    const API_BASE = "http://127.0.0.1:8000";

    let imageSrc = "https://placehold.co/200x200?text=No+Image";
    if (product.image !== null && product.image !== undefined && product.image !== "") {
        imageSrc = API_BASE + "/image-proxy?url=" + encodeURIComponent(product.image);
    }

  // onClick calls the handler passed down from App,
  // sending up the product's id
  function handleClick() {
    onCardClick(product.product_id);
  }

  return (
    <div className="product-card" onClick={handleClick}>

      <div className="card-image-wrap">
        <img
          src={imageSrc}
          alt={product.name}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={function(e) {
            e.target.src = "https://placehold.co/200x200?text=No+Image";
          }}
        />
      </div>

      <div className="card-body">
        <p className="card-name">{product.name}</p>
        <p className="card-price">{formattedPrice}</p>

        {starString !== "" && (
          <div className="card-rating">
            <span className="stars">{starString}</span>
            <span className="rating-value">{product.ratings}</span>
          </div>
        )}

        <p className="card-category">{product.category_name}</p>
      </div>

    </div>
  );
}

export default ProductCard;