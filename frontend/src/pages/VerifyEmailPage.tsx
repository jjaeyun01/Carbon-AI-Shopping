import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type State = "verifying" | "success" | "error";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const { verifyEmail } = useAuth();
  const navigate = useNavigate();

  const [state, setState] = useState<State>("verifying");
  const [errorMsg, setErrorMsg] = useState("");
  const attempted = useRef(false);

  useEffect(() => {
    if (attempted.current) return;
    attempted.current = true;

    const token = searchParams.get("token");
    if (!token) {
      setState("error");
      setErrorMsg("No verification token found in the URL.");
      return;
    }

    verifyEmail(token)
      .then(() => {
        setState("success");
        setTimeout(() => navigate("/"), 3000);
      })
      .catch((err: unknown) => {
        setState("error");
        setErrorMsg(err instanceof Error ? err.message : "Verification failed.");
      });
  }, [searchParams, verifyEmail, navigate]);

  return (
    <div
      style={{
        minHeight: "60vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
        textAlign: "center",
      }}
    >
      {state === "verifying" && (
        <>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⏳</div>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Verifying your email…</h1>
          <p style={{ color: "#6b7280" }}>Just a moment.</p>
        </>
      )}

      {state === "success" && (
        <>
          <div style={{ fontSize: 48, marginBottom: 16 }}>✅</div>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Email verified!</h1>
          <p style={{ color: "#6b7280", marginBottom: 24 }}>
            Welcome to Novera. You are now signed in.
          </p>
          <p style={{ color: "#9ca3af", fontSize: 14 }}>Redirecting to home in 3 seconds…</p>
        </>
      )}

      {state === "error" && (
        <>
          <div style={{ fontSize: 48, marginBottom: 16 }}>❌</div>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Verification failed</h1>
          <p style={{ color: "#6b7280", marginBottom: 24, maxWidth: 400 }}>{errorMsg}</p>
          <button
            onClick={() => navigate("/")}
            style={{
              background: "#16a34a",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "12px 24px",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: 15,
            }}
          >
            Go to Home
          </button>
        </>
      )}
    </div>
  );
}
