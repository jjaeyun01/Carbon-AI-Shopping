import { Link, useLocation, useParams } from "react-router-dom";

type OrderState = {
  order: {
    order_id: string;
    total_price: number;
    total_carbon_kg: number;
    status: string;
  };
  shipping: {
    full_name: string;
    email: string;
    address: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
  };
};

export default function OrderConfirmationPage() {
  const { id } = useParams();
  const location = useLocation();
  const state = location.state as OrderState | null;

  return (
    <section className="confirmPage">
      <div className="container">
        <div className="confirmCard">
          <div className="confirmIcon">✓</div>
          <h1 className="confirmTitle">Order Confirmed!</h1>
          <p className="confirmSub">
            Thank you{state?.shipping.full_name ? `, ${state.shipping.full_name.split(" ")[0]}` : ""}! Your order has been placed.
          </p>

          <div className="confirmDetails">
            <div className="confirmRow">
              <span>Order ID</span>
              <strong className="confirmOrderId">#{id ?? state?.order.order_id}</strong>
            </div>
            {state?.order.total_price != null && (
              <div className="confirmRow">
                <span>Order Total</span>
                <strong>${state.order.total_price.toFixed(2)}</strong>
              </div>
            )}
            {state?.order.total_carbon_kg != null && (
              <div className="confirmRow">
                <span>Carbon Footprint</span>
                <strong>{state.order.total_carbon_kg.toFixed(2)} kg CO₂e</strong>
              </div>
            )}
            {state?.shipping.email && (
              <div className="confirmRow">
                <span>Confirmation sent to</span>
                <strong>{state.shipping.email}</strong>
              </div>
            )}
          </div>

          <div className="confirmCarbonNote">
            <p>
              By choosing eco-conscious products, you're making a difference.
              Your purchase is tracked in our sustainability dashboard.
            </p>
          </div>

          <Link to="/" className="confirmHomeBtn">
            Continue Shopping
          </Link>
        </div>
      </div>
    </section>
  );
}
