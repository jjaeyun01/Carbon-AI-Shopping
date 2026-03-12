import { useEffect, useState } from "react";

type DashboardData = {
  total_carbon_saved: number;
  eco_choices_made: number;
  better_alternatives_chosen: number;
  sustainability_score: number;
  monthly_savings_kg: number;
  best_category: string;
  average_eco_score: number;
  saved_items: number;
};

export default function ImpactSection() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const res = await fetch("http://127.0.0.1:8000/dashboard/");

        if (!res.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const data = await res.json();
        setDashboard(data);
      } catch (err) {
        console.error(err);
        setError("Unable to load dashboard right now.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  return (
    <section id="impact" className="section impact">
      <div className="container impactGrid">
        <div className="impactLeft">
          <h2 className="impactTitle">Track Your Positive Impact</h2>
          <p className="impactDesc">
            Your dashboard helps you understand how small purchasing decisions
            add up over time. Compare products, choose better alternatives, and
            see your estimated carbon savings in one place.
          </p>

          {loading && <p className="impactMessage">Loading dashboard...</p>}
          {error && <p className="impactMessage impactError">{error}</p>}

          {dashboard && !loading && !error && (
            <div className="impactStats">
              <div className="impactStatCard">
                <div className="impactStatLabel">TOTAL CARBON SAVED</div>
                <div className="impactStatValue">
                  {dashboard.total_carbon_saved}
                  <span className="impactUnit"> kg</span>
                </div>
              </div>

              <div className="impactStatCard">
                <div className="impactStatLabel">ECO CHOICES MADE</div>
                <div className="impactStatValue">
                  {dashboard.eco_choices_made}
                  <span className="impactUnit"> items</span>
                </div>
              </div>

              <div className="impactStatCard">
                <div className="impactStatLabel">BETTER ALTERNATIVES CHOSEN</div>
                <div className="impactStatValue">
                  {dashboard.better_alternatives_chosen}
                  <span className="impactUnit"> switches</span>
                </div>
              </div>

              <div className="impactStatCard">
                <div className="impactStatLabel">SUSTAINABILITY SCORE</div>
                <div className="impactStatValue">
                  {dashboard.sustainability_score}
                  <span className="impactUnit"> / 100</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="impactRight">
          <div className="dashCard">
            <div className="dashTop">
              <div className="dashTitle">Sustainability Analytics</div>
              <div className="dashDots" aria-hidden="true">
                <span className="dotR" />
                <span className="dotY" />
                <span className="dotG" />
              </div>
            </div>

            <div className="dashGraph">
              <div className="graphBars">
                <div className="graphBar" style={{ height: "42%" }} />
                <div className="graphBar" style={{ height: "58%" }} />
                <div className="graphBar" style={{ height: "48%" }} />
                <div className="graphBar" style={{ height: "72%" }} />
                <div className="graphBar" style={{ height: "64%" }} />
                <div className="graphBar" style={{ height: "84%" }} />
              </div>
            </div>

            {dashboard && !loading && !error && (
              <div className="dashMiniGrid">
                <div className="dashMini">
                  <span className="dashMiniLabel">This Month</span>
                  <strong>{dashboard.monthly_savings_kg} kg</strong>
                </div>
                <div className="dashMini">
                  <span className="dashMiniLabel">Best Category</span>
                  <strong>{dashboard.best_category}</strong>
                </div>
                <div className="dashMini">
                  <span className="dashMiniLabel">Avg. Eco Score</span>
                  <strong>{dashboard.average_eco_score}</strong>
                </div>
                <div className="dashMini">
                  <span className="dashMiniLabel">Saved Items</span>
                  <strong>{dashboard.saved_items}</strong>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}