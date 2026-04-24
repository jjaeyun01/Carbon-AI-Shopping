import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../../context/CartContext";
import { trackUserAction } from "../../services/userActions";
import ProductImage from "../shared/ProductImage";

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

export default function CuratedSection() {
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const { addToCart } = useCart();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const res = await fetch("http://127.0.0.1:8000/products");

        if (!res.ok) {
          throw new Error("Failed to fetch products");
        }

        const data = await res.json();
        setItems(data.products ?? []);
      } catch (err) {
        console.error(err);
        setError("Unable to load products right now.");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  useEffect(() => {
    if (!search.trim()) return;

    const timeout = setTimeout(() => {
      trackUserAction({
        action_type: "search_products",
        query: search.trim(),
      });
    }, 500);

    return () => clearTimeout(timeout);
  }, [search]);

  const filteredItems = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    if (!keyword) return items.slice(0, 8);

    return items
      .filter((item) => {
        return (
          item.name.toLowerCase().includes(keyword) ||
          item.category.toLowerCase().includes(keyword) ||
          item.material.toLowerCase().includes(keyword) ||
          item.tag.toLowerCase().includes(keyword)
        );
      })
      .slice(0, 8);
  }, [items, search]);

  return (
    <section id="products" className="section curated">
      <div className="container">
        <div className="curatedTop">
          <div>
            <h2 className="curatedTitle">Top Picks</h2>
            <p className="curatedSub">Our most loved eco-certified products</p>
          </div>

          <button
            type="button"
            className="curatedLink"
            style={{ background: "none", border: "none", cursor: "pointer" }}
            onClick={() => navigate("/marketplace")}
          >
            View All →
          </button>
        </div>

        <div className="searchBarWrap">
          <input
            type="text"
            className="searchInput"
            placeholder="Search products, categories, materials..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading && <p className="sectionMessage">Loading products...</p>}
        {error && <p className="sectionMessage errorMessage">{error}</p>}

        {!loading && !error && filteredItems.length === 0 && (
          <p className="sectionMessage">No products found for "{search}".</p>
        )}

        {!loading && !error && filteredItems.length > 0 && (
          <div className="curatedGrid">
            {filteredItems.map((it) => (
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
                    <ProductImage
                      src={it.image_url}
                      alt={it.name}
                      category={it.category}
                      className="productImage"
                    />
                    <span className="productBadge">AI VERIFIED</span>
                    <div className="productEcoPill">Eco Score {it.eco_score}</div>
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
                        <div className="productSubTag">
                          {it.carbon_kg} kg CO₂e
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>

                <button
                  className="productAddToCart"
                  onClick={(e) => {
                    e.preventDefault();
                    addToCart({
                      id: it.id,
                      name: it.name,
                      price: it.price,
                      image_url: it.image_url,
                      material: it.material,
                      eco_score: it.eco_score,
                      carbon_kg: it.carbon_kg,
                    });
                  }}
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
