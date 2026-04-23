import { useEffect, useRef, useState } from "react";
import { useAuth } from "../../context/AuthContext";

type Props = {
  onClose: () => void;
  defaultTab?: "login" | "register";
};

export default function AuthModal({ onClose, defaultTab = "login" }: Props) {
  const { login, register } = useAuth();
  const [tab, setTab] = useState<"login" | "register">(defaultTab);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const overlayRef = useRef<HTMLDivElement>(null);

  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [registerForm, setRegisterForm] = useState({
    full_name: "",
    email: "",
    username: "",
    password: "",
    confirm: "",
  });

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(loginForm.email, loginForm.password);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (registerForm.password !== registerForm.confirm) {
      setError("Passwords do not match");
      return;
    }
    if (registerForm.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    setLoading(true);
    try {
      await register({
        email: registerForm.email,
        username: registerForm.username,
        full_name: registerForm.full_name,
        password: registerForm.password,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div
        className="authOverlay"
        ref={overlayRef}
        onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
      />
      <div className="authModal" role="dialog" aria-modal="true">
        <button className="authClose" onClick={onClose} aria-label="Close">✕</button>

        <div className="authTabs">
          <button
            className={`authTab${tab === "login" ? " active" : ""}`}
            onClick={() => { setTab("login"); setError(""); }}
          >
            Sign In
          </button>
          <button
            className={`authTab${tab === "register" ? " active" : ""}`}
            onClick={() => { setTab("register"); setError(""); }}
          >
            Sign Up
          </button>
        </div>

        {tab === "login" ? (
          <form className="authForm" onSubmit={handleLoginSubmit}>
            <h2 className="authTitle">Welcome back</h2>
            <p className="authSub">Sign in to your Novera account</p>

            <div className="formGroup">
              <label className="formLabel">Email</label>
              <input
                type="email"
                className="formInput"
                placeholder="you@example.com"
                value={loginForm.email}
                onChange={(e) => setLoginForm((p) => ({ ...p, email: e.target.value }))}
                required
              />
            </div>
            <div className="formGroup">
              <label className="formLabel">Password</label>
              <input
                type="password"
                className="formInput"
                placeholder="••••••••"
                value={loginForm.password}
                onChange={(e) => setLoginForm((p) => ({ ...p, password: e.target.value }))}
                required
              />
            </div>

            {error && <p className="authError">{error}</p>}

            <button type="submit" className="authSubmitBtn" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </button>

            <p className="authSwitch">
              Don't have an account?{" "}
              <button type="button" className="authSwitchLink" onClick={() => { setTab("register"); setError(""); }}>
                Sign up
              </button>
            </p>
          </form>
        ) : (
          <form className="authForm" onSubmit={handleRegisterSubmit}>
            <h2 className="authTitle">Create account</h2>
            <p className="authSub">Join Novera and shop sustainably</p>

            <div className="formGroup">
              <label className="formLabel">Full Name</label>
              <input
                type="text"
                className="formInput"
                placeholder="Jane Smith"
                value={registerForm.full_name}
                onChange={(e) => setRegisterForm((p) => ({ ...p, full_name: e.target.value }))}
                required
              />
            </div>
            <div className="formGroup">
              <label className="formLabel">Email</label>
              <input
                type="email"
                className="formInput"
                placeholder="you@example.com"
                value={registerForm.email}
                onChange={(e) => setRegisterForm((p) => ({ ...p, email: e.target.value }))}
                required
              />
            </div>
            <div className="formGroup">
              <label className="formLabel">Username</label>
              <input
                type="text"
                className="formInput"
                placeholder="janesmith"
                value={registerForm.username}
                onChange={(e) => setRegisterForm((p) => ({ ...p, username: e.target.value }))}
                required
              />
            </div>
            <div className="formGroup">
              <label className="formLabel">Password</label>
              <input
                type="password"
                className="formInput"
                placeholder="Min. 6 characters"
                value={registerForm.password}
                onChange={(e) => setRegisterForm((p) => ({ ...p, password: e.target.value }))}
                required
              />
            </div>
            <div className="formGroup">
              <label className="formLabel">Confirm Password</label>
              <input
                type="password"
                className="formInput"
                placeholder="••••••••"
                value={registerForm.confirm}
                onChange={(e) => setRegisterForm((p) => ({ ...p, confirm: e.target.value }))}
                required
              />
            </div>

            {error && <p className="authError">{error}</p>}

            <button type="submit" className="authSubmitBtn" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </button>

            <p className="authSwitch">
              Already have an account?{" "}
              <button type="button" className="authSwitchLink" onClick={() => { setTab("login"); setError(""); }}>
                Sign in
              </button>
            </p>
          </form>
        )}
      </div>
    </>
  );
}
