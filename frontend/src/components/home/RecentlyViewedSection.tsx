import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { trackUserAction } from "../../services/userActions";
import ProductImage from "../shared/ProductImage";

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

export default function RecentlyViewedSection() {
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecentProducts = async () => {
      try {
        setLoading(true);
        const res = await fetch("http://127.0.0.1:8000/user-actions/recent-products");

        if (!res.ok) {
          throw new Error("Failed to fetch recently viewed products");
        }

        const data = await res.json();
        setItems(data.products ?? []);
      } catch (err) {
        console.error(err);
        setItems([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentProducts();
  }, []);

  if (loading) {
    return (
      <section className="section recentSection">
        <div className="container">
          <p className="sectionMessage">Loading recently viewed products...</p>
        </div>
      </section>
    );
  }

  if (items.length === 0) {
    return null;
  }

  return (
    <section className="section recentSection">
      <div className="container">
        <div className="curatedTop">
          <div>
            <h2 className="curatedTitle">Recently Viewed</h2>
            <p className="curatedSub">
              Pick up where you left off and revisit products you explored.
            </p>
          </div>
        </div>

        <div className="curatedGrid">
          {items.map((it) => (
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
                  <ProductImage src={it.image_url} alt={it.name} category={it.category} className="productImage" />
                  <span className="productBadge">RECENTLY VIEWED</span>
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
                      <div className="productSubTag">Viewed recently</div>
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
      </div>
    </section>
  );
}