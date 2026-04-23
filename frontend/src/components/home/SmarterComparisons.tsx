import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Button from "../ui/Button";

const API_BASE = "http://127.0.0.1:8000";

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
  image_url?: string;
  description?: string;
};

type CatalogProduct = {
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
  image_url?: string;
  description?: string;
  source_url?: string;
};

type CompareFromUrlResponse = {
  base_product: CatalogProduct;
  recommendations: RecommendationProduct[];
  already_exists: boolean;
};

const EXAMPLE_URLS = [
  {
    label: "IKEA desk",
    url: "https://www.ikea.com/us/en/p/micke-desk-white-90214308/",
  },
  {
    label: "Everlane organic tee",
    url: "https://www.everlane.com/products/womens-organic-cotton-box-cut-tee-graystone",
  },
  {
    label: "EarthHero kit",
    url: "https://earthhero.com/products/hero-essentials-kit",
  },
];

function apiErrorMessage(data: unknown): string {
  if (data && typeof data === "object" && "detail" in data) {
    const d = (data as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      return d
        .map((x) => (typeof x === "object" && x && "msg" in x ? String((x as { msg: unknown }).msg) : String(x)))
        .join(" ");
    }
  }
  return "Something went wrong.";
}

function normalizeImageUrl(url: string | undefined): string | null {
  if (!url || typeof url !== "string") return null;
  const u = url.trim();
  if (!u) return null;
  if (u.startsWith("//")) return `https:${u}`;
  return u;
}

function truncateSnippet(text: string | undefined, max = 180): string {
  if (!text) return "";
  const t = text.replace(/\s+/g, " ").trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max - 1)}…`;
}

function CompareProductPhoto({ imageUrl }: { imageUrl?: string }) {
  const [broken, setBroken] = useState(false);
  const src = normalizeImageUrl(imageUrl);

  useEffect(() => {
    setBroken(false);
  }, [imageUrl]);

  if (!src || broken) {
    return <div className="compareMediaNoPhoto">No product image</div>;
  }

  return (
    <img
      src={src}
      alt=""
      className="compareMediaImg"
      referrerPolicy="no-referrer"
      loading="lazy"
      decoding="async"
      onError={() => setBroken(true)}
    />
  );
}

export default function SmarterComparisons() {
  const [urlInput, setUrlInput] = useState("");
  const [baseProduct, setBaseProduct] = useState<CatalogProduct | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationProduct[]>([]);
  const [alreadyExists, setAlreadyExists] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const topPick = recommendations[0] ?? null;
  const baseSnippet = baseProduct ? truncateSnippet(baseProduct.description) : "";
  const topSnippet = topPick ? truncateSnippet(topPick.description) : "";

  const maxCarbon = Math.max(
    baseProduct?.carbon_kg ?? 0,
    topPick?.carbon_kg ?? 0,
    0.01
  );
  const baseBarPct = Math.min(100, (baseProduct ? baseProduct.carbon_kg / maxCarbon : 0) * 100);
  const recBarPct = Math.min(100, (topPick ? topPick.carbon_kg / maxCarbon : 0) * 100);

  const runCompare = useCallback(async (url: string) => {
    const trimmed = url.trim();
    if (!trimmed) {
      setError("Paste a product page URL to analyze.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/products/compare-from-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmed }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(apiErrorMessage(data));
      }
      const parsed = data as CompareFromUrlResponse;
      setBaseProduct(parsed.base_product);
      setRecommendations(parsed.recommendations ?? []);
      setAlreadyExists(parsed.already_exists ?? false);
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : "Unable to analyze this URL.");
      setBaseProduct(null);
      setRecommendations([]);
      setAlreadyExists(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSample = useCallback(async () => {
    setError(null);
    setLoading(true);
    const sampleId = 4;
    try {
      const [baseRes, recRes] = await Promise.all([
        fetch(`${API_BASE}/products/${sampleId}`),
        fetch(`${API_BASE}/products/${sampleId}/recommendations`),
      ]);
      if (!baseRes.ok || !recRes.ok) {
        throw new Error("Sample data is unavailable. Try a product URL instead.");
      }
      const baseData = (await baseRes.json()) as CatalogProduct;
      const recData = (await recRes.json()) as { recommendations: RecommendationProduct[] };
      setBaseProduct(baseData);
      setRecommendations(recData.recommendations ?? []);
      setAlreadyExists(false);
      setUrlInput("");
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : "Unable to load sample.");
      setBaseProduct(null);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <section id="how" className="section compare">
      <div className="container">
        <h2 className="sectionTitle">How It Works</h2>
        <p className="sectionSub">
          Paste a real product page URL — we estimate its footprint and suggest a lower-impact alternative from our
          catalog when we can.
        </p>
        <p className="compareCatalogNote">
          <strong>What we can recognize:</strong> the scraper reads the page&apos;s title, description, images, and
          structured data (JSON-LD) when available, then saves that product into our catalog. Sites like{" "}
          <strong>Amazon</strong> often return a bot wall or minimal HTML, so names/images may be missing unless the
          page loads cleanly — there is no separate UPC/ASIN database lookup in this demo.
        </p>

        <div className="compareUrlPanel">
          <div className="compareUrlRow">
            <input
              type="url"
              className="searchInput compareUrlInput"
              placeholder="https://… (product page)"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runCompare(urlInput)}
              disabled={loading}
              aria-label="Product page URL"
            />
            <Button variant="primary" type="button" disabled={loading} onClick={() => runCompare(urlInput)}>
              {loading ? "Analyzing…" : "Analyze & compare"}
            </Button>
          </div>
          <div className="compareUrlExamples">
            <span className="compareUrlExamplesLabel">Try:</span>
            {EXAMPLE_URLS.map(({ label, url }) => (
              <button
                key={url}
                type="button"
                className="compareChip"
                disabled={loading}
                onClick={() => {
                  setUrlInput(url);
                  runCompare(url);
                }}
              >
                {label}
              </button>
            ))}
            <button type="button" className="compareChip compareChipGhost" disabled={loading} onClick={loadSample}>
              Sample (clothing swap)
            </button>
          </div>
          {alreadyExists && baseProduct && (
            <p className="compareUrlHint">This URL was already in our catalog — showing stored estimate and matches.</p>
          )}
        </div>

        {loading && <p className="sectionMessage">Analyzing product…</p>}
        {error && <p className="sectionMessage errorMessage">{error}</p>}

        {!loading && !error && baseProduct && (
          <div className="compareGrid">
            <div className="compareCard">
              <div className="compareTop">
                <span className="compareLabel">YOUR PRODUCT</span>
              </div>

              <div className="compareMedia">
                <div className="compareMediaPhotoWrap">
                  <CompareProductPhoto imageUrl={baseProduct.image_url} />
                </div>
                <div className="compareMediaFoot compareMediaFootCurrent">
                  <div className="compareMediaLabel">{baseProduct.name}</div>
                  {baseSnippet ? <p className="compareMediaSnippet">{baseSnippet}</p> : null}
                  {baseProduct.source_url?.startsWith("http") && (
                    <a
                      href={baseProduct.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="compareSourceLink"
                    >
                      View original listing ↗
                    </a>
                  )}
                </div>
              </div>

              <div className="compareStats">
                <div className="statRow">
                  <span>Est. carbon footprint</span>
                  <strong className="bad">{baseProduct.carbon_kg.toFixed(2)} kg CO₂e</strong>
                </div>
                <div className="bar">
                  <div className="barFill badFill" style={{ width: `${baseBarPct}%` }} />
                </div>

                <div className="detailGrid">
                  <div className="detailItem">
                    <span className="detailLabel">Category</span>
                    <strong>{baseProduct.category}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Material (est.)</span>
                    <strong>{baseProduct.material}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Shipping</span>
                    <strong>{baseProduct.shipping_type}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">ESG (model)</span>
                    <strong className="bad">{baseProduct.esg_rating}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Eco score</span>
                    <strong>{baseProduct.eco_score}</strong>
                  </div>
                  <div className="detailItem">
                    <span className="detailLabel">Price</span>
                    <strong>${baseProduct.price.toFixed(2)}</strong>
                  </div>
                </div>
              </div>
            </div>

            {topPick ? (
              <div className="compareCard betterCard">
                <div className="compareTop">
                  <span className="compareLabel">LOWER-IMPACT MATCH</span>
                  <span className="aiTag">AI SUGGESTION</span>
                </div>

                <div className="compareMedia">
                  <div className="compareMediaPhotoWrap">
                    <CompareProductPhoto imageUrl={topPick.image_url} />
                  </div>
                  <div className="compareMediaFoot compareMediaFootBetter">
                    <div className="compareMediaLabel">{topPick.name}</div>
                    {topSnippet ? <p className="compareMediaSnippet">{topSnippet}</p> : null}
                  </div>
                </div>

                <div className="compareStats">
                  <div className="statRow">
                    <span>Est. carbon footprint</span>
                    <strong className="good">{topPick.carbon_kg.toFixed(2)} kg CO₂e</strong>
                  </div>
                  <div className="bar">
                    <div className="barFill goodFill" style={{ width: `${recBarPct}%` }} />
                  </div>

                  <div className="detailGrid">
                    <div className="detailItem">
                      <span className="detailLabel">Category</span>
                      <strong>{topPick.category}</strong>
                    </div>
                    <div className="detailItem">
                      <span className="detailLabel">Material (est.)</span>
                      <strong>{topPick.material}</strong>
                    </div>
                    <div className="detailItem">
                      <span className="detailLabel">Shipping</span>
                      <strong>{topPick.shipping_type}</strong>
                    </div>
                    <div className="detailItem">
                      <span className="detailLabel">ESG (model)</span>
                      <strong className="good">{topPick.esg_rating}</strong>
                    </div>
                    <div className="detailItem">
                      <span className="detailLabel">Eco score</span>
                      <strong>{topPick.eco_score}</strong>
                    </div>
                    <div className="detailItem">
                      <span className="detailLabel">Price</span>
                      <strong>${topPick.price.toFixed(2)}</strong>
                    </div>
                  </div>

                  <div className="compareWhy">
                    Same category with similar price range, but better modeled eco score and lower estimated
                    emissions. Scores are heuristic — not a certified LCA.
                  </div>

                  <div className="compareAction">
                    <div className="miniRow">
                      <span>Eco score improvement</span>
                      <strong className="good">−{topPick.eco_gain_score} pts</strong>
                    </div>
                    <Link className="compareChooseLink" to={`/product/${topPick.id}`}>
                      Choose this instead
                    </Link>
                  </div>
                </div>
              </div>
            ) : (
              <div className="compareCard compareCardEmpty">
                <div className="compareTop">
                  <span className="compareLabel">LOWER-IMPACT MATCH</span>
                </div>
                <p className="compareEmptyBody">
                  We didn&apos;t find a catalog item in the <strong>same category</strong> with a clearly better
                  modeled eco score. Try another URL, or browse the marketplace for eco picks.
                </p>
                <Link className="compareChooseLink compareChooseLinkGhost" to="/marketplace">
                  Browse marketplace
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
