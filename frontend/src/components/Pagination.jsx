// src/components/Pagination.jsx

function Pagination({ page, totalPages, onPageChange }) {

  // ── Build the array of page numbers to display ─────────────────
  // Returns something like: [1, "...", 4, 5, 6, "...", 166]
  function buildPageNumbers() {

    // If total pages is small, just show all of them
    if (totalPages <= 7) {
      const allPages = [];
      let i = 1;
      while (i <= totalPages) {
        allPages.push(i);
        i = i + 1;
      }
      return allPages;
    }

    // Otherwise build the smart list
    const pageNumbers = [];

    // Always add page 1
    pageNumbers.push(1);

    // Add "..." if current page is far from the start
    // "far" means there's a gap between 1 and the left neighbour
    if (page > 3) {
      pageNumbers.push("...");
    }

    // Add the window around current page: one before, current, one after
    // Math.max and Math.min clamp the window so it never goes
    // below 2 or above totalPages - 1 (those are handled separately)
    const windowStart = Math.max(2, page - 1);
    const windowEnd   = Math.min(totalPages - 1, page + 1);

    let i = windowStart;
    while (i <= windowEnd) {
      pageNumbers.push(i);
      i = i + 1;
    }

    // Add "..." if current page is far from the end
    if (page < totalPages - 2) {
      pageNumbers.push("...");
    }

    // Always add the last page
    pageNumbers.push(totalPages);

    return pageNumbers;
  }

  // Build the array once so we can use it in the return below
  const pageNumbers = buildPageNumbers();

  return (
    <div className="pagination">

      {/* Previous button — disabled on page 1 */}
      <button
        className="page-btn"
        onClick={function() { onPageChange(page - 1); }}
        disabled={page === 1}
      >
        ← Prev
      </button>

      {/* Page number buttons and ellipsis */}
      <div className="page-numbers">
        {pageNumbers.map(function(p, index) {

          // If this entry is "..." render a span, not a button
          // We use index as key here because "..." has no unique ID
          // and its position in the array is stable
          if (p === "...") {
            return (
              <span key={"ellipsis-" + index} className="page-ellipsis">
                ...
              </span>
            );
          }

          // Otherwise render a page number button
          // Active page gets a different style via className
          return (
            <button
              key={p}
              className={"page-num" + (p === page ? " active" : "")}
              onClick={function() { onPageChange(p); }}
            >
              {p}
            </button>
          );
        })}
      </div>

      {/* Next button — disabled on last page */}
      <button
        className="page-btn"
        onClick={function() { onPageChange(page + 1); }}
        disabled={page === totalPages}
      >
        Next →
      </button>

    </div>
  );
}

export default Pagination;