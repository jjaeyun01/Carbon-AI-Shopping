import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { trackUserAction } from "../services/userActions";
import ProductImage from "../components/shared/ProductImage";

const API_BASE = "http://127.0.0.1:8000";

type Product = {
  id: number;
  name: string;
  category: string;
  price: number;
  material: string;
  eco_score: number;
  carbon_kg: number;
  esg_rating: string;
  tag: string;
  image_url: string;
};

const SORT_OPTIONS = [
  { value: "default",       label: "Default" },
  { value: "eco_score_asc", label: "Best Eco Score" },
  { value: "price_asc",     label: "Price: Low → High" },
  { value: "price_desc",    label: "Price: High → Low" },
];

const ALL_ESG = ["AAA", "AA", "A", "B+", "B", "C", "C-"];

const PRICE_PRESETS = [
  { label: "Under $25",    min: 0,   max: 25  },
  { label: "$25 – $75",   min: 25,  max: 75  },
  { label: "$75 – $200",  min: 75,  max: 200 },
  { label: "Over $200",   min: 200, max: Infinity },
];

// eco_score: lower = better eco
const ECO_PRESETS = [
  { label: "Excellent (≤20)", value: 20 },
  { label: "Good (≤40)",      value: 40 },
  { label: "Fair (≤60)",      value: 60 },
  { label: "All",             value: 999 },
];

type Filters = {
  priceMin: number;
  priceMax: number;
  esgRatings: Set<string>;
  maxEcoScore: number;
};

const DEFAULT_FILTERS: Filters = {
  priceMin:     0,
  priceMax:     Infinity,
  esgRatings:   new Set(ALL_ESG),
  maxEcoScore:  999,
};

function filtersAreDefault(f: Filters): boolean {
  return (
    f.priceMin === 0 &&
    f.priceMax === Infinity &&
    f.esgRatings.size === ALL_ESG.length &&
    f.maxEcoScore === 999
  );
}

// ── Active filter chips ────────────────────────────────────────────────────

type Chip = { label: string; onRemove: () => void };

function ActiveChips({
  chips,
  onClear,
}: {
  chips: Chip[];
  onClear: () => void;
}) {
  if (!chips.length) return null;
  return (
    <div className="filterChips">
      {chips.map((c) => (
        <button key={c.label} className="filterChip" onClick={c.onRemove}>
          {c.label} ✕
        </button>
      ))}
      <button className="filterChipClear" onClick={onClear}>
        Clear all
      </button>
    </div>
  );
}

// ── Sidebar ───────────────────────────────────────────────────────────────

function FilterSidebar({
  filters,
  esgCounts,
  onChange,
  onReset,
}: {
  filters: Filters;
  esgCounts: Record<string, number>;
  onChange: (f: Filters) => void;
  onReset: () => void;
}) {
  const toggleEsg = (rating: string) => {
    const next = new Set(filters.esgRatings);
    next.has(rating) ? next.delete(rating) : next.add(rating);
    onChange({ ...filters, esgRatings: next });
  };

  const setPrice = (min: number, max: number) =>
    onChange({ ...filters, priceMin: min, priceMax: max });

  const setEco = (v: number) => onChange({ ...filters, maxEcoScore: v });

  const activePricePreset = PRICE_PRESETS.find(
    (p) => p.min === filters.priceMin && p.max === filters.priceMax
  );

  return (
    <aside className="filterSidebar">
      <div className="filterSidebarHeader">
        <span className="filterSidebarTitle">Filters</span>
        {!filtersAreDefault(filters) && (
          <button className="filterResetBtn" onClick={onReset}>
            Reset
          </button>
        )}
      </div>

      {/* ── Price ── */}
      <div className="filterGroup">
        <div className="filterGroupLabel">Price</div>
        {PRICE_PRESETS.map((p) => (
          <button
            key={p.label}
            className={`filterOption${activePricePreset?.label === p.label ? " active" : ""}`}
            onClick={() =>
              activePricePreset?.label === p.label
                ? setPrice(0, Infinity)
                : setPrice(p.min, p.max)
            }
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* ── ESG Rating ── */}
      <div className="filterGroup">
        <div className="filterGroupLabel">ESG Rating</div>
        {ALL_ESG.map((r) => (
          <label key={r} className="filterCheckbox">
            <input
              type="checkbox"
              checked={filters.esgRatings.has(r)}
              onChange={() => toggleEsg(r)}
            />
            <span className={`esgBadge esgBadge--${r.replace("+", "plus")}`}>
              {r}
            </span>
            <span className="filterOptionCount">
              {esgCounts[r] ?? 0}
            </span>
          </label>
        ))}
      </div>

      {/* ── Eco Score ── */}
      <div className="filterGroup">
        <div className="filterGroupLabel">Eco Score</div>
        {ECO_PRESETS.map((p) => (
          <button
            key={p.label}
            className={`filterOption${filters.maxEcoScore === p.value ? " active" : ""}`}
            onClick={() => setEco(p.value)}
          >
            {p.label}
          </button>
        ))}
      </div>
    </aside>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────

export default function MarketplacePage() {
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("default");
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { addToCart } = useCart();

  useEffect(() => {
    fetch(`${API_BASE}/products/categories`)
      .then((r) => r.json())
      .then((d) => setCategories(d.categories ?? ["All"]))
      .catch(() => {});
  }, []);

  // Fetch when category or sort changes (price/esg/eco filters are client-side)
  useEffect(() => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (selectedCategory && selectedCategory !== "All")
      params.set("category", selectedCategory);
    if (sort && sort !== "default") params.set("sort", sort);

    fetch(`${API_BASE}/products?${params}`)
      .then((r) => { if (!r.ok) throw new Error("Failed"); return r.json(); })
      .then((d) => setAllProducts(d.products ?? []))
      .catch(() => setError("Unable to load products right now."))
      .finally(() => setLoading(false));
  }, [selectedCategory, sort]);

  // Track search
  useEffect(() => {
    if (!search.trim()) return;
    const t = setTimeout(() =>
      trackUserAction({ action_type: "search_products", query: search.trim() }), 500);
    return () => clearTimeout(t);
  }, [search]);

  // ESG counts (based on current category, no other filters)
  const esgCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const p of allProducts) {
      counts[p.esg_rating] = (counts[p.esg_rating] ?? 0) + 1;
    }
    return counts;
  }, [allProducts]);

  // Client-side filter + search
  const displayed = useMemo(() => {
    const kw = search.trim().toLowerCase();
    return allProducts.filter((p) => {
      if (p.price < filters.priceMin) return false;
      if (filters.priceMax !== Infinity && p.price > filters.priceMax) return false;
      if (!filters.esgRatings.has(p.esg_rating)) return false;
      if (p.eco_score > filters.maxEcoScore) return false;
      if (kw && !p.name.toLowerCase().includes(kw) &&
          !p.category.toLowerCase().includes(kw) &&
          !p.material.toLowerCase().includes(kw)) return false;
      return true;
    });
  }, [allProducts, filters, search]);

  // Active chips
  const chips = useMemo<Chip[]>(() => {
    const list: Chip[] = [];
    if (filters.priceMin > 0 || filters.priceMax !== Infinity) {
      const preset = PRICE_PRESETS.find(
        (p) => p.min === filters.priceMin && p.max === filters.priceMax
      );
      list.push({
        label: preset ? preset.label : `$${filters.priceMin}–$${filters.priceMax}`,
        onRemove: () => setFilters((f) => ({ ...f, priceMin: 0, priceMax: Infinity })),
      });
    }
    if (filters.esgRatings.size < ALL_ESG.length) {
      list.push({
        label: `ESG: ${[...filters.esgRatings].join(", ")}`,
        onRemove: () => setFilters((f) => ({ ...f, esgRatings: new Set(ALL_ESG) })),
      });
    }
    if (filters.maxEcoScore < 999) {
      const preset = ECO_PRESETS.find((p) => p.value === filters.maxEcoScore);
      list.push({
        label: preset ? `Eco: ${preset.label}` : `Eco ≤ ${filters.maxEcoScore}`,
        onRemove: () => setFilters((f) => ({ ...f, maxEcoScore: 999 })),
      });
    }
    return list;
  }, [filters]);

  const resetFilters = () => setFilters(DEFAULT_FILTERS);

  return (
    <section className="marketplacePage">
      <div className="container">
        <div className="marketplaceHeader">
          <div>
            <h1 className="marketplaceTitle">Marketplace</h1>
            <p className="marketplaceSub">
              {displayed.length.toLocaleString()} products · ranked by sustainability signals
            </p>
          </div>
          <Link to="/" className="backLink">← Home</Link>
        </div>

        {/* Category tabs */}
        <div className="categoryTabs">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`categoryTab${selectedCategory === cat ? " active" : ""}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search + sort + mobile filter toggle */}
        <div className="marketplaceControls">
          <div className="marketplaceFilters">
            <input
              type="text"
              className="searchInput marketplaceSearch"
              placeholder="Search products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select
              className="sortSelect"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <button
              className="filterToggleBtn"
              onClick={() => setSidebarOpen((v) => !v)}
            >
              {sidebarOpen ? "Hide Filters" : "Filters"}
              {!filtersAreDefault(filters) && (
                <span className="filterBadge">{chips.length}</span>
              )}
            </button>
          </div>
        </div>

        {/* Active filter chips */}
        <ActiveChips chips={chips} onClear={resetFilters} />

        {/* Layout: sidebar + grid */}
        <div className={`marketplaceLayout${sidebarOpen ? " sidebarOpen" : ""}`}>
          {sidebarOpen && (
            <FilterSidebar
              filters={filters}
              esgCounts={esgCounts}
              onChange={setFilters}
              onReset={resetFilters}
            />
          )}

          <div className="marketplaceGridWrapper">
            {loading && <p className="sectionMessage">Loading products...</p>}
            {error   && <p className="sectionMessage errorMessage">{error}</p>}
            {!loading && !error && displayed.length === 0 && (
              <p className="sectionMessage">No products match your filters.</p>
            )}
            {!loading && !error && displayed.length > 0 && (
              <div className="marketplaceGrid">
                {displayed.map((it) => (
                  <article key={it.id} className="productCard">
                    <Link
                      to={`/product/${it.id}`}
                      className="productCardLink"
                      onClick={() =>
                        trackUserAction({ action_type: "open_product_from_grid", product_id: it.id })
                      }
                    >
                      <div className="productMedia">
                        <ProductImage
                          src={it.image_url}
                          alt={it.name}
                          category={it.category}
                          className="productImage"
                        />
                        <span className="productBadge">{it.esg_rating}</span>
                        <div className="productEcoPill">Eco {it.eco_score}</div>
                      </div>
                      <div className="productBody">
                        <div className="productMeta">
                          <span>{it.category}</span>
                          <span>{it.material}</span>
                        </div>
                        <h3 className="productName">{it.name}</h3>
                        <div className="productPrice">${it.price.toFixed(2)}</div>
                        <div className="productBottom">
                          <div>
                            <div className="productTag">{it.tag}</div>
                            <div className="productSubTag">{it.carbon_kg} kg CO₂e</div>
                          </div>
                        </div>
                      </div>
                    </Link>
                    <button
                      className="productAddToCart"
                      onClick={() =>
                        addToCart({
                          id: it.id, name: it.name, price: it.price,
                          image_url: it.image_url, material: it.material,
                          eco_score: it.eco_score, carbon_kg: it.carbon_kg,
                        })
                      }
                    >
                      Add to Cart
                    </button>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
