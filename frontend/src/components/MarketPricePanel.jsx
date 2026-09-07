import { useState } from "react";
import { AlertTriangle, Search, TrendingUp } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getMarketPrices } from "../api/marketPrices";
import { StatePanel } from "./ui";

function formatPrice(value) {
  return value === null || value === undefined ? "—" : `₹${Number(value).toLocaleString("en-IN")}`;
}

export default function MarketPricePanel({ compact = false, listings = [] }) {
  const [filters, setFilters] = useState({ commodity: "Tomato", state: "Tamil Nadu", district: "Chennai" });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load(event) {
    event?.preventDefault(); setLoading(true); setError("");
    try { setData(await getMarketPrices(filters)); }
    catch (err) { setError(err.message || "Market prices unavailable"); }
    finally { setLoading(false); }
  }

  const latest = data?.markets?.[0];
  const chartData = [...(data?.markets || [])].reverse().slice(-12);
  const localListing = data
    ? listings.find((item) => item.crop?.trim().toLowerCase() === data.commodity?.trim().toLowerCase())
    : null;
  return <section className="card market-price">
    <div className="card-header"><div><p className="eyebrow" style={{color: "#9cedb1"}}>External market reference</p><h2 className="section-heading">Current Mandi Prices</h2></div><TrendingUp /></div>
    <div className="card-body">
      <form className="form-grid" onSubmit={load} style={{gridTemplateColumns: compact ? "1fr" : undefined}}>
        <div className="field"><label htmlFor="market-commodity" style={{color: "white"}}>Commodity</label><input id="market-commodity" value={filters.commodity} onChange={(e) => setFilters({...filters, commodity: e.target.value})} required /></div>
        <div className="field"><label htmlFor="market-state" style={{color: "white"}}>State</label><input id="market-state" value={filters.state} onChange={(e) => setFilters({...filters, state: e.target.value})} required /></div>
        <div className="field"><label htmlFor="market-district" style={{color: "white"}}>District</label><input id="market-district" value={filters.district} onChange={(e) => setFilters({...filters, district: e.target.value})} required /></div>
        <div className="field"><label htmlFor="market-name" style={{color: "white"}}>Market (optional)</label><input id="market-name" value={filters.market || ""} onChange={(e) => setFilters({...filters, market: e.target.value})} /></div>
        <button className="button secondary" disabled={loading}><Search size={17} />{loading ? "Checking…" : "Check latest available"}</button>
      </form>
      <StatePanel loading={loading} error={error} empty={!data} emptyText="Choose a commodity and location to load the latest available mandi observation.">
        {data && <>
          <div className="split" style={{marginTop: "1rem"}}><div><strong>{data.commodity}</strong><div className="muted">{data.state} · {data.district}</div></div>{data.age_days > 1 && <span className="status-badge warning"><AlertTriangle size={13} /> {data.age_days} days old</span>}</div>
          {latest ? <><div className="market-grid">{localListing && <div className="market-value"><small>Your listing price</small><strong>{formatPrice(localListing.price_per_unit)} / {localListing.unit}</strong></div>}<div className="market-value"><small>Mandi modal reference</small><strong>{formatPrice(latest.modal_price)} / quintal</strong></div><div className="market-value"><small>Mandi range</small><strong>{formatPrice(latest.min_price)}–{formatPrice(latest.max_price)} / quintal</strong></div><div className="market-value"><small>Market</small><strong>{latest.market}</strong></div><div className="market-value"><small>Market data updated</small><strong>{latest.date}</strong></div></div>
          {localListing && <p className="market-note">Your listing and the external mandi observation are shown separately. AgroSave never changes your price automatically.</p>}
          {chartData.length > 1 && <div style={{height: 175, marginTop: "1rem"}}><ResponsiveContainer width="100%" height="100%"><LineChart data={chartData}><XAxis dataKey="date" tick={{fill: "rgba(255,255,255,.65)", fontSize: 11}} axisLine={false} tickLine={false} /><YAxis tick={{fill: "rgba(255,255,255,.65)", fontSize: 11}} axisLine={false} tickLine={false} width={48} /><Tooltip /><Line type="monotone" dataKey="modal_price" stroke="#9cedb1" strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer></div>}</> : <div className="notice warning" style={{marginTop: "1rem"}}>No observations were returned for these filters.</div>}
          {data.stale_cache && <div className="notice warning" style={{marginTop: "1rem"}}>CEDA is unavailable. Showing the last successfully retrieved response.</div>}
        </>}
      </StatePanel>
      <div className="ceda-credit"><span>Source: CEDA Agri Market Data (Agmarknet), Centre for Economic Data &amp; Analysis, Ashoka University. Reference only; no endorsement implied.</span><img className="ceda-logo" src="https://viz.ceda.ashoka.edu.in/assets/logo.png" alt="CEDA" /></div>
    </div>
  </section>;
}
