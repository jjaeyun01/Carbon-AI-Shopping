import { Routes, Route } from "react-router-dom";
import Header from "./components/layout/Header";
import HeroSection from "./components/home/HeroSection";
import SmarterComparisons from "./components/home/SmarterComparisons";
import ImpactSection from "./components/home/ImpactSection";
import CuratedSection from "./components/home/CuratedSection";
import Footer from "./components/layout/Footer";
import ProductDetailPage from "./pages/ProductDetailPage.tsx";
import RecentlyViewedSection from "./components/home/RecentlyViewedSection";
import MostViewedSection from "./components/home/MostViewedSection";

function HomePage() {
  return (
    <>
      <HeroSection />
      <SmarterComparisons />
      <ImpactSection />
      <MostViewedSection />
      <RecentlyViewedSection />
      <CuratedSection />
    </>
  );
}

export default function App() {
  return (
    <div className="appShell">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/product/:id" element={<ProductDetailPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}