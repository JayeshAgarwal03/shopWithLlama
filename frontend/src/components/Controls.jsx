// src/components/Controls.jsx

function Controls({
  searchDraft,
  onSearchDraftChange,
  onSearchCommit,
  categories,
  selectedCategory,
  onCategoryChange
}) {

  // Fires when user presses a key inside the search input.
  // We only care about Enter — everything else is handled by onChange.
  function handleKeyDown(e) {
    if (e.key === "Enter") {
      onSearchCommit();
    }
  }

  // Fires every time the input value changes (every keystroke).
  // e.target.value is the current text in the input box.
  function handleSearchChange(e) {
    onSearchDraftChange(e.target.value);
  }

  // Fires when the dropdown selection changes.
  // e.target.value is the selected option's value.
  function handleCategoryChange(e) {
    onCategoryChange(e.target.value);
  }

  return (
    <div className="controls-bar">
      <div className="controls-inner">

        {/* Search input + button */}
        <div className="search-group">
          <input
            type="text"
            className="search-input"
            placeholder="Search products..."
            value={searchDraft}
            onChange={handleSearchChange}
            onKeyDown={handleKeyDown}
          />
          <button
            className="search-btn"
            onClick={onSearchCommit}
          >
            Search
          </button>
        </div>

        {/* Category dropdown */}
        {/* value={selectedCategory} makes this a controlled input too */}
        <select
          className="category-select"
          value={selectedCategory}
          onChange={handleCategoryChange}
        >
          <option value="">All Categories</option>

          {categories.map(function(cat) {
            return (
              <option key={cat.id} value={cat.name}>
                {cat.name}
              </option>
            );
          })}

        </select>

      </div>
    </div>
  );
}

export default Controls;