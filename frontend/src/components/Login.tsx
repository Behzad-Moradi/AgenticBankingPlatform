import { useState, type FormEvent } from "react";
import { AgentNetworkIcon, LockIcon, ShieldIcon } from "./Icons";

interface LoginProps {
  onLogin: (email: string, password: string) => Promise<void>;
  onRegister: (firstName: string, lastName: string, email: string, password: string) => Promise<void>;
}

export function Login({ onLogin, onRegister }: LoginProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function changeMode(nextMode: "login" | "register") {
    setMode(nextMode);
    setError("");
    setPassword("");
    setConfirmPassword("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");

    if (mode === "register" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      if (mode === "register") {
        await onRegister(firstName, lastName, email, password);
      } else {
        await onLogin(email, password);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : mode === "register" ? "Registration failed." : "Sign in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-story" aria-label="Product introduction">
        <div className="brand brand-light"><span className="brand-mark"><AgentNetworkIcon /></span><span>Agentic Banking Platform</span></div>
        <div className="story-copy">
          <span className="eyebrow">AI-powered banking</span>
          <h1>Banking help,<br />without the runaround.</h1>
          <p>Your secure assistant for everyday banking, account applications, and card support.</p>
        </div>
        <div className="trust-row">
          <span><ShieldIcon /> Protected sessions</span>
          <span><LockIcon /> Secure sign-in</span>
        </div>
        <div className="orb orb-one" /><div className="orb orb-two" />
      </section>

      <section className="login-panel">
        <div className="mobile-brand brand"><span className="brand-mark"><AgentNetworkIcon /></span><span>Agentic Banking Platform</span></div>
        <form className="login-card" onSubmit={submit}>
          <div className="auth-tabs" role="tablist" aria-label="Authentication options">
            <button type="button" role="tab" aria-selected={mode === "login"} className={mode === "login" ? "active" : ""} onClick={() => changeMode("login")}>Sign in</button>
            <button type="button" role="tab" aria-selected={mode === "register"} className={mode === "register" ? "active" : ""} onClick={() => changeMode("register")}>Create account</button>
          </div>
          <div className="form-heading">
            <span className="eyebrow dark">{mode === "login" ? "Welcome back" : "Get started"}</span>
            <h2>{mode === "login" ? "Sign in to continue" : "Create your profile"}</h2>
            <p>{mode === "login" ? "Use the credentials registered with the banking platform." : "Register a customer profile to explore the banking assistant."}</p>
          </div>
          {mode === "register" && (
            <div className="name-fields">
              <label>
                First name
                <input
                  type="text"
                  autoComplete="given-name"
                  placeholder="First name"
                  maxLength={100}
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                  required
                  autoFocus
                />
              </label>
              <label>
                Last name
                <input
                  type="text"
                  autoComplete="family-name"
                  placeholder="Last name"
                  maxLength={100}
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                  required
                />
              </label>
            </div>
          )}
          <label>
            Email address
            <input
              type="email"
              autoComplete={mode === "login" ? "username" : "email"}
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoFocus={mode === "login"}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              placeholder={mode === "login" ? "Enter your password" : "At least 8 characters"}
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {mode === "register" && (
            <label>
              Confirm password
              <input
                type="password"
                autoComplete="new-password"
                placeholder="Enter your password again"
                minLength={8}
                maxLength={128}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            </label>
          )}
          {error && <div className="alert error" role="alert">{error}</div>}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading
              ? <><span className="spinner" /> {mode === "register" ? "Creating account…" : "Signing in…"}</>
              : mode === "register" ? "Create account" : "Sign in securely"}
          </button>
          <p className="privacy-note"><LockIcon /> Your token is kept only for this browser session.</p>
        </form>
      </section>
    </main>
  );
}
