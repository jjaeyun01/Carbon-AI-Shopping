import logo from "../../assets/images/logo/noveralogo.png";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footerInner">
        <div className="footerBrand">
          <img className="footerLogo" src={logo} alt="Novera logo" />
          <span className="footerName">NOVERA</span>
        </div>

        <nav className="footerNav">
          <a href="#privacy">Privacy Policy</a>
          <a href="#terms">Terms of Service</a>
          <a href="#contact">Contact</a>
        </nav>

        <div className="footerCopy">
          © {new Date().getFullYear()} Novera AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}