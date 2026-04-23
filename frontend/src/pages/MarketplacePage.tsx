import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { trackUserAction } from "../services/userActions";

const API_BASE = "http://127.0.0.1:8000";

type Product = {
  id: number;
  name: string;
  category: string;
  price: number;
  material: string;
  eco_score: number;
  carbon_kg: number;
  tag: string;
  image_url: string;
};

const SORT_OPTIONS = [
  { value: "default", label: "Default" },
  { value: "eco_score_asc", label: "Best Eco Score" },
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
];

export default function MarketplacePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("default");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { addToCart } = useCart();

  useEffect(() => {
    fetch(`${API_BASE}/products/categories`)
      .then((r) => r.json())
      .then((d) => setCategories(d.categories ?? ["All"]))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (selectedCategory && selectedCategory !== "All") {
      params.set("category", selectedCategory);
    }
    if (sort && sort !== "default") {
      params.set("sort", sort);
    }

    fetch(`${API_BASE}/products?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error("Failed");
        return r.json();
      })
      .then((d) => setProducts(d.products ?? []))
      .catch(() => setError("Unable to load products right now."))
      .finally(() => setLoading(false));
  }, [selectedCategory, sort]);

  useEffect(() => {
    if (!search.trim()) return;
    const t = setTimeout(() => {
      trackUserAction({ action_type: "search_products", query: search.trim() });
    }, 500);
    return () => clearTimeout(t);
  }, [search]);

  const displayed = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    if (!keyword) return products;
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(keyword) ||
        p.category.toLowerCase().includes(keyword) ||
        p.material.toLowerCase().includes(keyword)
    );
  }, [products, search]);

  return (
    <section className="marketplacePage">
      <div className="container">
        <div className="marketplaceHeader">
          <div>
            <h1 className="marketplaceTitle">Marketplace</h1>
            <p className="marketplaceSub">
              {displayed.length} products · ranked by sustainability signals
            </p>
          </div>
          <Link to="/" className="backLink">← Home</Link>
        </div>

        <div className="marketplaceControls">
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
          </div>
        </div>

        {loading && <p className="sectionMessage">Loading products...</p>}
        {error && <p className="sectionMessage errorMessage">{error}</p>}

        {!loading && !error && displayed.length === 0 && (
          <p className="sectionMessage">No products found.</p>
        )}

        {!loading && !error && displayed.length > 0 && (
          <div className="marketplaceGrid">
            {displayed.map((it) => (
              <article key={it.id} className="productCard">
                <Link
                  to={`/product/${it.id}`}
                  className="productCardLink"
                  onClick={() =>
                    trackUserAction({
                      action_type: "open_product_from_grid",
                      product_id: it.id,
                    })
                  }
                >
                  <div className="productMedia">
                    <img
                      src={it.image_url}
                      alt={it.name}
                      className="productImage"
                    />
                    <span className="productBadge">AI VERIFIED</span>
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
                      id: it.id,
                      name: it.name,
                      price: it.price,
                      image_url: it.image_url,
                      material: it.material,
                      eco_score: it.eco_score,
                      carbon_kg: it.carbon_kg,
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
    </section>
  );
}
