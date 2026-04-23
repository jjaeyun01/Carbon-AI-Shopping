import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

const API_BASE = "http://127.0.0.1:8000";

type FormData = {
  full_name: string;
  email: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
};

const EMPTY_FORM: FormData = {
  full_name: "",
  email: "",
  address: "",
  city: "",
  state: "",
  zip_code: "",
  country: "United States",
};

export default function CheckoutPage() {
  const { items, subtotal, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState<FormData>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalCarbon = items.reduce((s, i) => s + i.carbon_kg * i.quantity, 0);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) return;

    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/orders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: items.map((i) => ({
            product_id: i.id,
            name: i.name,
            price: i.price,
            quantity: i.quantity,
            material: i.material,
            carbon_kg: i.carbon_kg,
          })),
          shipping: form,
          user_id: user?.id ?? null,
        }),
      });

      if (!res.ok) throw new Error("Order failed");

      const data = await res.json();
      clearCart();
      navigate(`/order-confirmation/${data.order_id}`, {
        state: { order: data, shipping: form },
      });
    } catch {
      setError("Failed to place order. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (items.length === 0) {
    return (
      <section className="checkoutPage">
        <div className="container">
          <div className="checkoutEmpty">
            <h2>Your cart is empty</h2>
            <Link to="/" className="backLink">← Back to shopping</Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="checkoutPage">
      <div className="container">
        <div className="checkoutBackRow">
          <Link to="/" className="backLink">← Continue Shopping</Link>
        </div>

        <h1 className="checkoutHeading">Checkout</h1>

        <div className="checkoutGrid">
          <form className="checkoutForm" onSubmit={handleSubmit}>
            <h2 className="checkoutFormTitle">Shipping Information</h2>

            <div className="formGroup">
              <label className="formLabel" htmlFor="full_name">Full Name</label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                className="formInput"
                value={form.full_name}
                onChange={handleChange}
                required
                placeholder="Jane Smith"
              />
            </div>

            <div className="formGroup">
              <label className="formLabel" htmlFor="email">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                className="formInput"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="jane@example.com"
              />
            </div>

            <div className="formGroup">
              <label className="formLabel" htmlFor="address">Street Address</label>
              <input
                id="address"
                name="address"
                type="text"
                className="formInput"
                value={form.address}
                onChange={handleChange}
                required
                placeholder="123 Green Street"
              />
            </div>

            <div className="formRow">
              <div className="formGroup">
                <label className="formLabel" htmlFor="city">City</label>
                <input
                  id="city"
                  name="city"
                  type="text"
                  className="formInput"
                  value={form.city}
                  onChange={handleChange}
                  required
                  placeholder="San Francisco"
                />
              </div>
              <div className="formGroup">
                <label className="formLabel" htmlFor="state">State</label>
                <input
                  id="state"
                  name="state"
                  type="text"
                  className="formInput"
                  value={form.state}
                  onChange={handleChange}
                  required
                  placeholder="CA"
                />
              </div>
              <div className="formGroup">
                <label className="formLabel" htmlFor="zip_code">ZIP Code</label>
                <input
                  id="zip_code"
                  name="zip_code"
                  type="text"
                  className="formInput"
                  value={form.zip_code}
                  onChange={handleChange}
                  required
                  placeholder="94102"
                />
              </div>
            </div>

            <div className="formGroup">
              <label className="formLabel" htmlFor="country">Country</label>
              <input
                id="country"
                name="country"
                type="text"
                className="formInput"
                value={form.country}
                onChange={handleChange}
                required
              />
            </div>

            {error && <p className="formError">{error}</p>}

            <button
              type="submit"
              className="checkoutSubmitBtn"
              disabled={submitting}
            >
              {submitting ? "Placing Order..." : `Place Order — $${subtotal.toFixed(2)}`}
            </button>
          </form>

          <div className="checkoutSummary">
            <h2 className="checkoutFormTitle">Order Summary</h2>
            <ul className="summaryList">
              {items.map((item) => (
                <li key={item.id} className="summaryItem">
                  <div className="summaryItemImage">
                    <img src={item.image_url} alt={item.name} />
                  </div>
                  <div className="summaryItemInfo">
                    <p className="summaryItemName">{item.name}</p>
                    <p className="summaryItemMeta">
                      Qty: {item.quantity} · {item.material}
                    </p>
                    <p className="summaryItemCarbon">
                      {(item.carbon_kg * item.quantity).toFixed(2)} kg CO₂e
                    </p>
                  </div>
                  <span className="summaryItemPrice">
                    ${(item.price * item.quantity).toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>

            <div className="summaryTotals">
              <div className="summaryRow">
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="summaryRow">
                <span>Shipping</span>
                <span className="summaryGreen">Free</span>
              </div>
              <div className="summaryRow summaryTotal">
                <strong>Total</strong>
                <strong>${subtotal.toFixed(2)}</strong>
              </div>
            </div>

            <div className="summaryCarbon">
              <span className="summaryCarbonLabel">Total Carbon Footprint</span>
              <strong className="summaryCarbonValue">{totalCarbon.toFixed(2)} kg CO₂e</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
