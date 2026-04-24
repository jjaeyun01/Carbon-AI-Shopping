import { createContext, useCallback, useContext, useEffect, useState } from "react";

export type AuthUser = {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
};

type RegisterResult = {
  requiresVerification: true;
  email: string;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<RegisterResult>;
  logout: () => void;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
};

type RegisterData = {
  email: string;
  username: string;
  full_name: string;
  password: string;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const API_BASE = "http://127.0.0.1:8000";
const TOKEN_KEY = "novera_token";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    if (!storedToken) {
      setLoading(false);
      return;
    }
    fetch(`${API_BASE}/auth/me?token=${storedToken}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) {
          setToken(storedToken);
          setUser(data);
        } else {
          localStorage.removeItem(TOKEN_KEY);
        }
      })
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Login failed");
    }
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  }, []);

  const register = useCallback(async (form: RegisterData): Promise<RegisterResult> => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Registration failed");
    }
    const data = await res.json();
    return { requiresVerification: true, email: data.email };
  }, []);

  const verifyEmail = useCallback(async (verifyToken: string) => {
    const res = await fetch(`${API_BASE}/auth/verify-email?token=${verifyToken}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Verification failed");
    }
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  }, []);

  const resendVerification = useCallback(async (email: string) => {
    const res = await fetch(`${API_BASE}/auth/resend-verification`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to resend verification email");
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, register, logout, verifyEmail, resendVerification }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
