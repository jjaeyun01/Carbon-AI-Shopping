import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { trackUserAction } from "../../services/userActions";

type Product = {
  id: number;
  name: string;
  category: string;
  price: number;
  material: string;
  eco_score: number;
  tag: string;
  image_url: string;
};

export default function CuratedSection() {
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

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
            <h2 className="curatedTitle">Curated for You</h2>
            <p className="curatedSub">
              Discover lower-carbon products ranked by sustainability signals,
              price fit, and category relevance.
            </p>
          </div>

          <a className="curatedLink" href="#">
            View Marketplace <span aria-hidden="true">›</span>
          </a>
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
          <p className="sectionMessage">No products found for “{search}”.</p>
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
                    <img
                      src={it.image_url}
                      alt={it.name}
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
                          Better alternative available
                        </div>
                      </div>

                      <span className="productAdd" aria-hidden="true">
                        →
                      </span>
                    </div>
                  </div>
                </Link>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}