import Button from "../ui/Button";
import logo from "../../assets/images/logo/noveralogo.png";

export default function Header() {
  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <header className="header">
      <div className="container headerInner">
        <a className="brand" href="#">
          <img src={logo} alt="Novera logo" className="logo" />
          <span className="brandText">NOVERA</span>
        </a>

        <nav className="nav">
          <button type="button" className="navLink" onClick={() => scrollTo("how")}>
            How It Works
          </button>
          <button type="button" className="navLink" onClick={() => scrollTo("products")}>
            Products
          </button>
          <button type="button" className="navLink" onClick={() => scrollTo("impact")}>
            Impact
          </button>
          <Button variant="primary" type="button" onClick={() => alert("Sign in coming soon")}>
            Sign In
          </Button>
        </nav>
      </div>
    </header>
  );
}