import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

export function StatusBadge({ status }) {
  const normalized = String(status || "UNKNOWN").toUpperCase();
  const success = ["ACTIVE", "APPROVED", "COMPLETED", "DELIVERED", "CONNECTED", "OK", "SELECTED"].includes(normalized);
  const warning = ["PENDING", "ASSIGNED", "PICKED_UP", "IN_TRANSIT", "PARTIAL"].includes(normalized);
  const danger = ["REJECTED", "CANCELLED", "VOIDED", "UNAVAILABLE", "DEGRADED"].includes(normalized);
  const className = success ? "success" : warning ? "warning" : danger ? "danger" : "neutral";
  return <span className={`status-badge ${className}`}>{normalized.replaceAll("_", " ")}</span>;
}

export function StatePanel({ loading, error, empty, emptyText = "Nothing to show yet.", children }) {
  if (loading) return <div className="state-panel"><div><LoaderCircle size={28} className="spin" /><p>Loading…</p></div></div>;
  if (error) return <div className="state-panel"><div><AlertCircle size={28} /><p>{error}</p></div></div>;
  if (empty) return <div className="state-panel"><div><Inbox size={28} /><p>{emptyText}</p></div></div>;
  return children;
}

export function MetricCard({ label, value, icon: Icon }) {
  return <div className="card metric-card"><div className="metric-top"><span>{label}</span><span className="metric-icon"><Icon size={19} /></span></div><div className="metric-value">{value}</div></div>;
}

export function PageHeading({ eyebrow, title, description, action }) {
  return <div className="page-heading"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h1 className="page-title">{title}</h1>{description && <p className="page-intro">{description}</p>}</div>{action}</div>;
}
