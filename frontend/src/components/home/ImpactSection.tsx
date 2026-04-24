import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";

const API_BASE = "http://127.0.0.1:8000";

type DashboardData = {
  authenticated: boolean;
  has_purchases: boolean;
  total_carbon_saved_kg: number;
  eco_choices_made: number;
  better_alternatives_chosen: number;
  sustainability_score: number;
  monthly_savings_kg: number;
  best_category: string;
  average_eco_score: number;
  total_orders: number;
  monthly_carbon_data: number[];
};

// ── Bar chart ─────────────────────────────────────────────────────────────────

function BarChart({ data, hasRealData }: { data: number[]; hasRealData: boolean }) {
  const max = Math.max(...data, 0.1);

  // Build last-6-month labels relative to today
  const now = new Date();
  const monthLabels = Array.from({ length: 6 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (5 - i), 1);
    return d.toLocaleString("en-US", { month: "short" });
  });

  return (
    <div className="chartWrapper">
      <div className="chartMeta">
        <span className="chartTitle">Monthly CO₂ saved</span>
        <span className="chartUnit">kg CO₂</span>
      </div>
      <div className="graphBars">
        {data.map((val, i) => {
          const pct = Math.max(8, Math.round((val / max) * 100));
          const isLatest = i === data.length - 1;
          return (
            <div key={i} className="graphBarCol">
              {hasRealData && val > 0 && (
                <span className="graphBarVal">{val.toFixed(1)}</span>
              )}
              <div
                className={`graphBar${isLatest ? " graphBarActive" : ""}`}
                style={{ height: `${pct}%` }}
              />
              <span className={`graphBarLabel${isLatest ? " graphBarLabelActive" : ""}`}>
                {monthLabels[i]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── States ────────────────────────────────────────────────────────────────────

function UnauthenticatedState({ onSignIn }: { onSignIn: () => void }) {
  return (
    <div className="impactAuthPrompt">
      <div className="impactAuthIcon">🌿</div>
      <p className="impactAuthMsg">
        Sign in to track <strong>your</strong> personal carbon impact and see how your
        eco choices add up over time.
      </p>
      <button className="impactSignInBtn" onClick={onSignIn}>
        Sign in to see your impact
      </button>
    </div>
  );
}

function EmptyPurchasesState() {
  return (
    <div className="impactAuthPrompt">
      <div className="impactAuthIcon">🛒</div>
      <p className="impactAuthMsg">
        Your impact dashboard is ready! Make your first eco purchase and
        we&apos;ll track your carbon savings here.
      </p>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ImpactSection() {
  const { user, token, loading: authLoading } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  useEffect(() => {
    if (authLoading) return;

    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const url = token
          ? `${API_BASE}/dashboard/?token=${token}`
          : `${API_BASE}/dashboard/`;
        const res = await fetch(url);
        if (res.ok) setDashboard(await res.json());
      } catch {
        // silently ignore
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [token, authLoading]);

  // Open the auth modal in the Header (dispatch a custom event)
  const handleSignInClick = () => {
    window.dispatchEvent(new CustomEvent("novera:open-auth", { detail: { tab: "login" } }));
  };

  const isAuthenticated = !!user;
  const hasPurchases = dashboard?.has_purchases ?? false;
  const showStats = isAuthenticated && hasPurchases && dashboard;

  // Bar chart data: real or placeholder skeleton
  const hasRealChartData = !!(showStats && dashboard.monthly_carbon_data.some((v) => v > 0));
  const barData = hasRealChartData
    ? dashboard!.monthly_carbon_data
    : [0.42, 0.58, 0.48, 0.72, 0.64, 0.84].map((v) => v * 10);

  return (
    <section id="impact" className="section impact">
      <div className="container impactGrid">
        {/* ── Left panel ── */}
        <div className="impactLeft">
          <h2 className="impactTitle">Track Your Positive Impact</h2>
          <p className="impactDesc">
            Your dashboard helps you understand how small purchasing decisions add
            up over time. Compare products, choose better alternatives, and see
            your estimated carbon savings in one place.
          </p>

          {loading || authLoading ? (
            <p className="impactMessage">Loading your impact data…</p>
          ) : !isAuthenticated ? (
            <UnauthenticatedState onSignIn={handleSignInClick} />
          ) : !hasPurchases ? (
            <EmptyPurchasesState />
          ) : (
            <div className="impactStats">
              <div className="impactStatCard">
                <div className="impactStatLabel">TOTAL CARBON SAVED</div>
                <div className="impactStatValue">
                  {dashboard!.total_carbon_saved_kg.toFixed(1)}
                  <span className="impactUnit"> kg CO₂</span>
                </div>
              </div>

              <div className="impactStatCard">
                <div className="impactStatLabel">ECO CHOICES MADE</div>
                <div className="impactStatValue">
                  {dashboard!.eco_choices_made}
                  <span className="impactUnit"> items</span>
                </div>
              </div>

              <div className="impactStatCard">
                <div className="impactStatLabel">ORDERS PLACED</div>
                <div className="impactStatValue">
                  {dashboard!.better_alternatives_chosen}
                  <span className="impactUnit"> orders</span>
                </div>
              </div>

              <div className="impactStatCard">
                <div className="impactStatLabel">SUSTAINABILITY SCORE</div>
                <div className="impactStatValue">
                  {dashboard!.sustainability_score}
                  <span className="impactUnit"> / 100</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Right panel ── */}
        <div className="impactRight">
          <div className="dashCard">
            <div className="dashTop">
              <div className="dashTitle">
                {isAuthenticated
                  ? `${user!.full_name ?? user!.username}'s Analytics`
                  : "Sustainability Analytics"}
              </div>
              <div className="dashDots" aria-hidden="true">
                <span className="dotR" />
                <span className="dotY" />
                <span className="dotG" />
              </div>
            </div>

            <div className="dashGraph">
              <BarChart data={barData} hasRealData={hasRealChartData} />
            </div>

            <div className="dashMiniGrid">
              <div className="dashMini">
                <span className="dashMiniLabel">This Month</span>
                <strong>
                  {showStats ? `${dashboard!.monthly_savings_kg.toFixed(1)} kg` : "—"}
                </strong>
              </div>
              <div className="dashMini">
                <span className="dashMiniLabel">Best Category</span>
                <strong>{showStats ? dashboard!.best_category : "—"}</strong>
              </div>
              <div className="dashMini">
                <span className="dashMiniLabel">Avg. Eco Score</span>
                <strong>{showStats ? dashboard!.average_eco_score : "—"}</strong>
              </div>
              <div className="dashMini">
                <span className="dashMiniLabel">Total Orders</span>
                <strong>{showStats ? dashboard!.total_orders : "—"}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {authModalOpen && (
        <div onClick={() => setAuthModalOpen(false)} />
      )}
    </section>
  );
}
