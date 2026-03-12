const API_BASE = "http://127.0.0.1:8000";

type TrackUserActionPayload = {
  action_type:
    | "view_product"
    | "view_recommendation"
    | "search_products"
    | "open_product_from_grid";
  product_id?: number;
  source_product_id?: number;
  query?: string;
};

export async function trackUserAction(payload: TrackUserActionPayload) {
  try {
    const res = await fetch(`${API_BASE}/user-actions/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    console.log("Tracked action:", data);
  } catch (error) {
    console.error("Failed to track user action:", error);
  }
}