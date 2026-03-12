import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { trackUserAction } from "../services/userActions";

type Product = {
  id: number;
  name: string;
  category: string;
  price: number;
  material: string;
  eco_score: number;
  carbon_kg: number;
  esg_rating: string;
  shipping_type: string;
  tag: string;
  image_url: string;
  description: string;
};

type Recommendation = {
  id: number;
  name: string;
  category: string;
  price: number;
  material: string;
  eco_score: number;
  carbon_kg: number;
  esg_rating: string;
  shipping_type: string;
  tag: string;
  image_url: string;
  similarity_score: number;
  eco_gain_score: number;
};

type RecommendationResponse = {
  base_product_id: number;
  base_product_name: string;
  recommendations: Recommendation[];
};

export default function ProductDetailPage() {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const trackedProductRef = useRef<number | null>(null);

  const API_BASE = "http://127.0.0.1:8000";

  useEffect(() => {
    if (!id) return;

    const numericId = Number(id);

    const fetchProductData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [productRes, recommendationRes] = await Promise.all([
          fetch(`${API_BASE}/products/${numericId}`),
          fetch(`${API_BASE}/products/${numericId}/recommendations`),
        ]);

        if (!productRes.ok) {
          throw new Error("Failed to fetch product");
        }

        const productData = await productRes.json();
        setProduct(productData);

        if (trackedProductRef.current !== numericId) {
          trackUserAction({
            action_type: "view_product",
            product_id: numericId,
          });
          trackedProductRef.current = numericId;
        }

        if (recommendationRes.ok) {
          const recommendationData: RecommendationResponse =
            await recommendationRes.json();
          setRecommendations(recommendationData.recommendations ?? []);
        } else {
          setRecommendations([]);
        }
      } catch (err) {
        console.error(err);
        setError("Unable to load product details right now.");
      } finally {
        setLoading(false);
      }
    };

    fetchProductData();
  }, [id]);

  if (loading) {
    return (
      <section className="detailPage">
        <div className="container">
          <p className="sectionMessage">Loading product details...</p>
        </div>
      </section>
    );
  }

  if (error || !product) {
    return (
      <section className="detailPage">
        <div className="container">
          <p className="sectionMessage errorMessage">
            {error ?? "Product not found."}
          </p>
          <Link to="/" className="backLink">
            ← Back to home
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="detailPage">
      <div className="container">
        <div className="detailBackRow">
          <Link to="/" className="backLink">
            ← Back to home
          </Link>
        </div>

        <div className="detailGrid">
          <div className="detailImageCard">
            <img
              src={product.image_url}
              alt={product.name}
              className="detailImage"
            />
          </div>

          <div className="detailInfoCard">
            <div className="detailTopMeta">
              <span className="detailCategory">{product.category}</span>
              <span className="detailTag">{product.tag}</span>
            </div>

            <h1 className="detailTitle">{product.name}</h1>
            <p className="detailDescription">{product.description}</p>

            <div className="detailPrice">${product.price.toFixed(2)}</div>

            <div className="detailStatsGrid">
              <div className="detailStat">
                <span className="detailStatLabel">Material</span>
                <strong>{product.material}</strong>
              </div>
              <div className="detailStat">
                <span className="detailStatLabel">Eco Score</span>
                <strong>{product.eco_score}</strong>
              </div>
              <div className="detailStat">
                <span className="detailStatLabel">Carbon Footprint</span>
                <strong>{product.carbon_kg} kg CO₂e</strong>
              </div>
              <div className="detailStat">
                <span className="detailStatLabel">ESG Rating</span>
                <strong>{product.esg_rating}</strong>
              </div>
              <div className="detailStat">
                <span className="detailStatLabel">Shipping</span>
                <strong>{product.shipping_type}</strong>
              </div>
              <div className="detailStat">
                <span className="detailStatLabel">Recommendation Signal</span>
                <strong>{product.tag}</strong>
              </div>
            </div>
          </div>
        </div>

        <div className="detailRecommendationSection">
          <div className="detailSectionHeader">
            <h2 className="detailSectionTitle">Better Alternatives</h2>
            <p className="detailSectionSub">
              Similar products with lower carbon impact.
            </p>
          </div>

          {recommendations.length === 0 ? (
            <p className="sectionMessage">
              No lower-carbon alternatives found for this item.
            </p>
          ) : (
            <div className="detailRecommendationGrid">
              {recommendations.map((item) => (
                <article key={item.id} className="detailRecommendationCard">
                  <div className="detailRecommendationMedia">
                    <img
                      src={item.image_url}
                      alt={item.name}
                      className="detailRecommendationImage"
                    />
                    <div className="detailRecommendationBadge">AI SUGGESTED</div>
                  </div>

                  <div className="detailRecommendationBody">
                    <div className="detailRecommendationMeta">
                      <span>{item.category}</span>
                      <span>{item.material}</span>
                    </div>

                    <h3 className="detailRecommendationName">{item.name}</h3>
                    <div className="detailRecommendationPrice">
                      ${item.price.toFixed(2)}
                    </div>

                    <div className="detailRecommendationInfo">
                      <span>Eco Score {item.eco_score}</span>
                      <span>{item.carbon_kg} kg CO₂e</span>
                    </div>

                    <div className="detailRecommendationGain">
                      Estimated improvement: -{item.eco_gain_score} eco score
                    </div>

                    <Link
                      to={`/product/${item.id}`}
                      className="detailRecommendationLink"
                      onClick={() =>
                        trackUserAction({
                          action_type: "view_recommendation",
                          product_id: item.id,
                          source_product_id: product.id,
                        })
                      }
                    >
                      View details →
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}