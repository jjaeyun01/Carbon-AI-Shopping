import Badge from "../ui/Badge";
import Button from "../ui/Button";
import main from "../../assets/images/main/mainImage.png";

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="container heroGrid">
        <div>
          <Badge>AI-POWERED SUSTAINABLE SHOPPING</Badge>

          <h1 className="h1">
            Shop Smarter. <br />
            <span className="h1Accent">Choose Lower Carbon.</span>
          </h1>

          <p className="lead">
            Novera helps you compare products by sustainability signals like material,
            carbon footprint, and sourcing so you can find better alternatives without
            sacrificing quality, style, or price.
          </p>

          <div className="heroActions">
            <Button
              variant="primary"
              onClick={() =>
                document.getElementById("products")?.scrollIntoView({ behavior: "smooth" })
              }
            >
              Explore Products
            </Button>

            <Button
              onClick={() =>
                document.getElementById("how")?.scrollIntoView({ behavior: "smooth" })
              }
            >
              See How It Works
            </Button>
          </div>

          <div className="heroMiniStats">
            <div className="heroMiniStat">
              <strong>1,200+ </strong>
              <span>Products scored</span>
            </div>
            <div className="heroMiniStat">
              <strong>32% </strong>
              <span>Avg. lower-carbon swap</span>
            </div>
            <div className="heroMiniStat">
              <strong>AI </strong>
              <span>Comparison engine</span>
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