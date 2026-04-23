import { Link } from "react-router-dom";
import Badge from "../ui/Badge";
import Button from "../ui/Button";
import main from "../../assets/images/main/mainImage.png";

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="container heroGrid">
        <div>
          <Badge>AI-Powered Eco Shopping</Badge>

          <h1 className="h1">
            Your everyday
            <br />
            products —{" "}
            <span className="h1Accent">reimagined</span>
            <br />
            for the planet.
          </h1>

          <p className="lead">
            Compare products by materials, carbon footprint, and sourcing. Novera
            surfaces lower-impact alternatives so you can shop with confidence.
          </p>

          <div className="heroActions">
            <Button
              variant="primary"
              onClick={() =>
                document.getElementById("how")?.scrollIntoView({ behavior: "smooth" })
              }
            >
              Find My Eco Alternative →
            </Button>

            <Link className="btn" to="/marketplace">
              Browse Shop
            </Link>
          </div>

          <div className="heroMiniStats">
            <div className="heroMiniStat">
              <strong>2,400+</strong>
              <span>Eco Products</span>
            </div>
            <div className="heroMiniStat">
              <strong>87%</strong>
              <span>Avg. CO₂ Saved</span>
            </div>
            <div className="heroMiniStat">
              <strong>150k+</strong>
              <span>Happy Shoppers</span>
            </div>
          </div>
        </div>

        <div className="heroCard">
          <img src={main} alt="Novera sustainable shopping visual" className="heroImg" />
        </div>
      </div>
    </section>
  );
}