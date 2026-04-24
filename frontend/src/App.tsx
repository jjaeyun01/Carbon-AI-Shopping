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
import CheckoutPage from "./pages/CheckoutPage.tsx";
import OrderConfirmationPage from "./pages/OrderConfirmationPage.tsx";
import MarketplacePage from "./pages/MarketplacePage.tsx";
import CartDrawer from "./components/cart/CartDrawer.tsx";
import { CartProvider } from "./context/CartContext.tsx";
import { AuthProvider } from "./context/AuthContext.tsx";
import VerifyEmailPage from "./pages/VerifyEmailPage.tsx";

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
    <AuthProvider>
      <CartProvider>
        <div className="appShell">
          <Header />
          <CartDrawer />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/product/:id" element={<ProductDetailPage />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/order-confirmation/:id" element={<OrderConfirmationPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </CartProvider>
    </AuthProvider>
  );
}
