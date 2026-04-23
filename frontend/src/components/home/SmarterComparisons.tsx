import { useEffect, useState } from "react";
import Button from "../ui/Button";

type RecommendationProduct = {
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
  similarity_score: number;
  eco_gain_score: number;
};

type RecommendationResponse = {
  base_product_id: number;
  base_product_name: string;
  recommendations: RecommendationProduct[];
};

type BaseProduct = {
  id: number;
  name: string;
  material: string;
  eco_score: number;
  carbon_kg: number;
  esg_rating: string;
  shipping_type: string;
};

export default function SmarterComparisons() {
  const [baseProduct, setBaseProduct] = useState<BaseProduct | null>(null);
  const [recommended, setRecommended] = useState<RecommendationProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const baseProductId = 5;

  useEffect(() => {
    const fetchComparisonData = async () => {
      try {
        setLoading(true);

        const [baseRes, recRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/products/${baseProductId}`),
          fetch(`http://127.0.0.1:8000/products/${baseProductId}/recommendations`),
        ]);

        if (!baseRes.ok || !recRes.ok) {
          throw new Error("Failed to fetch comparison data");
        }

        const baseData = await baseRes.json();
        const recData: RecommendationResponse = await recRes.json();

        setBaseProduct(baseData);
        setRecommended(recData.recommendations?.[0] ?? null);
      } catch (err) {
        console.error(err);
        setError("Unable to load comparison right now.");
      } finally {
        setLoading(false);
      }
    };

    fetchComparisonData();
  }, []);

  return (
    <section id="how" className="section compare">
      <div className="container">
        <h2 className="sectionTitle">How It Works</h2>
        <p className="sectionSub">Three steps to greener shopping — see a live comparison.</p>

        {loading && <p className="sectionMessage">Loading comparison...</p>}
        {error && <p className="sectionMessage errorMessage">{error}</p>}

        {!loading && !error && baseProduct && recommended && (
          <div className="compareGrid">
            <div className="compareCard">
              <div className="compareTop">
                <span className="compareLabel">CURRENT CONSIDERATION</span>
              </div>

              <div className="compareMedia currentMedia">
                <div className="compareMediaLabel">{baseProduct.name}</div>
              </div>

              <div className="compareStats">
                <div className="statRow">
                  <span>Carbon Footprint</span>
                  <strong className="bad">
                    {baseProduct.carbon_kg} kg CO₂e
                  </strong>
                </div>
                <div className="bar">
                  <div className="barFill badFill" style={{ width: "82%" }} />
                </div>

                <div className="detailGrid">
                  <div className="detailItem">
                    <span className="detailLabel">Material</span>
                    <strong>{baseProduct.material}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Shipping</span>
                    <strong>{baseProduct.shipping_type}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">ESG Rating</span>
                    <strong className="bad">{baseProduct.esg_rating}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Eco Score</span>
                    <strong>{baseProduct.eco_score}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div className="compareCard betterCard">
              <div className="compareTop">
                <span className="compareLabel">BETTER ALTERNATIVE</span>
                <span className="aiTag">AI SUGGESTION</span>
              </div>

              <div className="compareMedia betterMedia">
                <div className="compareMediaLabel">{recommended.name}</div>
              </div>

              <div className="compareStats">
                <div className="statRow">
                  <span>Carbon Footprint</span>
                  <strong className="good">
                    {recommended.carbon_kg} kg CO₂e
                  </strong>
                </div>
                <div className="bar">
                  <div className="barFill goodFill" style={{ width: "28%" }} />
                </div>

                <div className="detailGrid">
                  <div className="detailItem">
                    <span className="detailLabel">Material</span>
                    <strong>{recommended.material}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Shipping</span>
                    <strong>{recommended.shipping_type}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">ESG Rating</span>
                    <strong className="good">{recommended.esg_rating}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Eco Score</span>
                    <strong>{recommended.eco_score}</strong>
                  </div>
                </div>

                <div className="compareWhy">
                  Why recommended: similar category and price range, but lower
                  carbon impact and better sustainability score.
                </div>

                <div className="compareAction">
                  <div className="miniRow">
                    <span>Estimated reduction</span>
                    <strong className="good">
                      -{recommended.eco_gain_score} eco score
                    </strong>
                  </div>
                  <Button variant="primary" type="button">
                    Choose This Instead
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}