import { useState, useEffect } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import logo from "../../assets/images/logo/noveralogo.png";
import AuthModal from "../auth/AuthModal";
import { useAuth } from "../../context/AuthContext";
import { useCart } from "../../context/CartContext";

export default function Header() {
  const { user, logout, loading } = useAuth();
  const { itemCount, openCart } = useCart();
  const [authModal, setAuthModal] = useState<"login" | "register" | null>(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Allow other components (e.g. ImpactSection) to open the auth modal
  useEffect(() => {
    const handler = (e: Event) => {
      const tab = (e as CustomEvent<{ tab: "login" | "register" }>).detail?.tab ?? "login";
      setAuthModal(tab);
    };
    window.addEventListener("novera:open-auth", handler);
    return () => window.removeEventListener("novera:open-auth", handler);
  }, []);

  const scrollTo = (id: string) => {
    if (window.location.pathname !== "/") {
      navigate("/");
      setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }), 100);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <>
      <header className={`header${scrolled ? " headerScrolled" : ""}`}>
        <div className="container headerInner">
          <Link className="brand" to="/">
            <span className="brandMark" aria-hidden>
              <img src={logo} alt="" className="logo" />
            </span>
            <span className="brandText">Novera</span>
          </Link>

          <nav className="nav">
            <NavLink className="navLink" end to="/">
              Home
            </NavLink>
            <button type="button" className="navLink navLinkOptional" onClick={() => scrollTo("how")}>
              Find Eco Alternative
            </button>
            <NavLink className="navLink" to="/marketplace">
              Shop
            </NavLink>

            <button
              type="button"
              className="navCartBtn"
              onClick={openCart}
              aria-label={`Open cart, ${itemCount} items`}
            >
              <span className="navCartLabel">Cart</span>
              {itemCount > 0 && <span className="cartBadge">{itemCount}</span>}
            </button>

            {!loading && (
              user ? (
                <div className="userMenu">
                  <button
                    className="userMenuBtn"
                    onClick={() => setUserMenuOpen((v) => !v)}
                  >
                    <span className="userAvatar">
                      {(user.full_name || user.username).charAt(0).toUpperCase()}
                    </span>
                    <span className="userMenuName">{user.full_name?.split(" ")[0] ?? user.username}</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M6 9l6 6 6-6" /></svg>
                  </button>
                  {userMenuOpen && (
                    <div className="userDropdown">
                      <div className="userDropdownInfo">
                        <strong>{user.full_name ?? user.username}</strong>
                        <span>{user.email}</span>
                      </div>
                      <button
                        className="userDropdownItem danger"
                        onClick={() => { logout(); setUserMenuOpen(false); }}
                      >
                        Sign Out
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  type="button"
                  className="btnPrimary"
                  style={{ padding: "10px 24px", borderRadius: "14px", fontSize: "14px" }}
                  onClick={() => setAuthModal("login")}
                >
                  Sign In
                </button>
              )
            )}
          </nav>
        </div>
      </header>

      {authModal && (
        <AuthModal
          defaultTab={authModal}
          onClose={() => setAuthModal(null)}
        />
      )}
    </>
  );
}
