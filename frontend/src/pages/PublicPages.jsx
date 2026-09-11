import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, BarChart3, Handshake, ShieldCheck, ShoppingBasket, Truck } from "lucide-react";
import Logo from "../components/Logo";
import { useAuth, ROLE_HOME } from "../context/AuthContext";

export function LandingPage() {
  return <>
    <section className="landing-hero">
      <img className="hero-image" src="/agrosave-hero.png" alt="Indian farmer carrying freshly harvested greens in a cultivated field" />
      <nav className="public-nav"><Logo /><div className="public-links"><a href="#how-it-works">How it works</a><a href="#platform">Platform</a><Link className="button secondary small" to="/login">Sign in</Link></div></nav>
      <div className="hero-content"><p className="eyebrow" style={{color: "#8fe4a7"}}>Direct agriculture, visible decisions</p><h1>From field to buyer, with fewer blind spots.</h1><p>AgroSave connects verified farmers, consumers, bulk buyers, finance, and logistics through one shared marketplace—supported by market-price references and activity forecasting.</p><div className="hero-actions"><Link className="button" to="/register">Join the marketplace <ArrowRight size={18} /></Link><Link className="button secondary" to="/login">Open your workspace</Link></div></div>
    </section>
    <section className="story-strip" id="how-it-works">{["Farmer lists", "Buyer orders", "Farmer confirms", "Logistics collects", "Route is optimized", "Delivery is traced"].map((step, index) => <div className="story-step" key={step}><span className="story-number">{index + 1}</span><span>{step}</span></div>)}</section>
    <section className="landing-section" id="platform"><p className="eyebrow">One connected platform</p><h2>Useful visibility across the agricultural supply chain.</h2><div className="feature-grid">
      <div className="card feature-card"><ShoppingBasket /><h3>Shared marketplace</h3><p>Verified farmer listings flow into one marketplace used by consumers and bulk buyers.</p></div>
      <div className="card feature-card"><BarChart3 /><h3>Decision support</h3><p>Mandi reference prices and market-activity forecasts support decisions without changing farmer prices automatically.</p></div>
      <div className="card feature-card"><Truck /><h3>Traceable logistics</h3><p>Orders move through assignment, pickup, transit, delivery, and recorded handoffs.</p></div>
    </div><div className="feature-grid">
      <div className="card feature-card"><ShieldCheck /><h3>Verified participation</h3><p>Farmer and financier documents are reviewed through the existing admin workflow.</p></div>
      <div className="card feature-card"><Handshake /><h3>Bulk finance</h3><p>Bulk buyers can request financing and use approved relationships for eligible orders.</p></div>
    </div></section>
    <footer className="public-footer"><Logo /><span>SIH26033 AgriMarketplace prototype</span></footer>
  </>;
}

function AuthAside({ register }) {
  return <aside className="auth-aside"><Logo /><div className="auth-copy"><p className="eyebrow" style={{color: "#8fe4a7"}}>AgroSave marketplace</p><h1>{register ? "Build a fairer route to market." : "Welcome back to the field."}</h1><p>{register ? "Create a buyer or farmer account and join the same connected order and logistics flow." : "Access listings, orders, finance, forecasts, and delivery operations from your role workspace."}</p></div><small>Secure access through the existing FastAPI JWT service.</small></aside>;
}

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  if (user) return <Navigate to={ROLE_HOME[user.role]} replace />;

  async function submit(event) {
    event.preventDefault(); setError(""); setSubmitting(true);
    try {
      const current = await login(form);
      const requested = location.state?.from;
      navigate(requested && requested.startsWith(ROLE_HOME[current.role]) ? requested : ROLE_HOME[current.role], { replace: true });
    } catch (err) { setError(err.message); }
    finally { setSubmitting(false); }
  }

  return <div className="auth-page"><AuthAside /><main className="auth-panel"><div className="auth-form"><p className="eyebrow">Secure sign in</p><h2>Access your workspace</h2><p>Use the email and password registered with AgroSave.</p>{error && <div className="notice error">{error}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="email">Email</label><input id="email" type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} placeholder="you@example.com" /></div><div className="field"><label htmlFor="password">Password</label><input id="password" type="password" autoComplete="current-password" required value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} placeholder="Your password" /></div><button className="button" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button></form><p className="auth-switch">New to AgroSave? <Link to="/register">Create an account</Link></p></div></main></div>;
}

export function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "FARMER" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);
  if (user) return <Navigate to={ROLE_HOME[user.role]} replace />;

  async function submit(event) {
    event.preventDefault(); setError(""); setSubmitting(true);
    try { await register(form); setSuccess("Account created. You can now sign in."); setTimeout(() => navigate("/login"), 900); }
    catch (err) { setError(err.message); }
    finally { setSubmitting(false); }
  }

  return <div className="auth-page"><AuthAside register /><main className="auth-panel"><div className="auth-form"><p className="eyebrow">Create an account</p><h2>Join AgroSave</h2><p>Public registration is available for farmers and buyers. Operational roles are provisioned separately.</p>{error && <div className="notice error">{error}</div>}{success && <div className="notice">{success}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="role">I am joining as</label><select id="role" value={form.role} onChange={(e) => setForm({...form, role: e.target.value})}><option value="FARMER">Farmer</option><option value="CONSUMER">Consumer</option><option value="BULK_BUYER">Bulk buyer</option><option value="FINANCIER">Financier</option></select></div><div className="field"><label htmlFor="name">Full name</label><input id="name" required value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} /></div><div className="field"><label htmlFor="register-email">Email</label><input id="register-email" type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} /></div><div className="field"><label htmlFor="register-password">Password</label><input id="register-password" type="password" minLength="8" autoComplete="new-password" required value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} /><small className="muted">Use at least 8 characters.</small></div><button className="button" disabled={submitting}>{submitting ? "Creating account…" : "Create account"}</button></form><p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p></div></main></div>;
}
