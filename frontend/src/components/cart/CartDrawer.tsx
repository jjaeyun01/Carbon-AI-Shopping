import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../../context/CartContext";

export default function CartDrawer() {
  const { items, itemCount, subtotal, removeFromCart, updateQuantity, closeCart, isOpen } =
    useCart();

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      <div className="cartOverlay" onClick={closeCart} />
      <aside className="cartDrawer">
        <div className="cartHeader">
          <h2 className="cartTitle">Your Cart ({itemCount})</h2>
          <button className="cartClose" onClick={closeCart} aria-label="Close cart">
            ✕
          </button>
        </div>

        {items.length === 0 ? (
          <div className="cartEmpty">
            <p>Your cart is empty.</p>
            <button className="cartEmptyLink" onClick={closeCart}>
              Browse Products →
            </button>
          </div>
        ) : (
          <>
            <ul className="cartList">
              {items.map((item) => (
                <li key={item.id} className="cartItem">
                  <div className="cartItemImage">
                    <img src={item.image_url} alt={item.name} />
                  </div>
                  <div className="cartItemInfo">
                    <p className="cartItemName">{item.name}</p>
                    <p className="cartItemMeta">
                      {item.material} · {item.carbon_kg} kg CO₂e
                    </p>
                    <div className="cartItemRow">
                      <div className="cartQty">
                        <button
                          className="cartQtyBtn"
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        >
                          −
                        </button>
                        <span>{item.quantity}</span>
                        <button
                          className="cartQtyBtn"
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        >
                          +
                        </button>
                      </div>
                      <span className="cartItemPrice">
                        ${(item.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                    <button
                      className="cartItemRemove"
                      onClick={() => removeFromCart(item.id)}
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>

            <div className="cartFooter">
              <div className="cartSubtotal">
                <span>Subtotal</span>
                <strong>${subtotal.toFixed(2)}</strong>
              </div>
              <p className="cartCarbonNote">
                Total carbon: {items.reduce((s, i) => s + i.carbon_kg * i.quantity, 0).toFixed(2)} kg CO₂e
              </p>
              <Link
                to="/checkout"
                className="cartCheckoutBtn"
                onClick={closeCart}
              >
                Proceed to Checkout
              </Link>
            </div>
          </>
        )}
      </aside>
    </>
  );
}
