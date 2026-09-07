import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Search, ShoppingCart } from "lucide-react";
import { PageHeading, StatePanel, StatusBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { getMarketplaceProduce, listMarketplace } from "../api/marketplace";
import { createOrder, reviewOrder } from "../api/orders";
import { listRelationships } from "../api/finance";
import { ProduceVisual } from "./ProducePages";

export function MarketplacePage() {
  const { user } = useAuth();
  const [filters, setFilters] = useState({crop: "", location: "", max_price: ""});
  const [query, setQuery] = useState({});
  const state = useApiData(() => listMarketplace(query), [query]);
  const prefix = user.role === "BULK_BUYER" ? "/app/buyer" : "/app/consumer";
  return <><PageHeading eyebrow="Verified produce" title="Marketplace" description="Only active, in-stock listings from approved farmers appear here." /><form className="filters" onSubmit={(e) => {e.preventDefault(); setQuery(filters);}}><div className="field"><label htmlFor="filter-crop">Crop</label><input id="filter-crop" value={filters.crop} onChange={(e) => setFilters({...filters, crop: e.target.value})} /></div><div className="field"><label htmlFor="filter-location">Location</label><input id="filter-location" value={filters.location} onChange={(e) => setFilters({...filters, location: e.target.value})} /></div><div className="field"><label htmlFor="filter-price">Maximum price</label><input id="filter-price" type="number" min="0" value={filters.max_price} onChange={(e) => setFilters({...filters, max_price: e.target.value})} /></div><button className="button" style={{alignSelf: "end"}}><Search size={17} />Filter</button></form><StatePanel loading={state.loading} error={state.error} empty={!state.data?.length} emptyText="No verified produce matches these filters."><div className="produce-grid">{state.data?.map((item) => <article className="card produce-card" key={item.id}><ProduceVisual item={item} /><div className="card-body"><div className="split"><h3>{item.crop}</h3><StatusBadge status={item.status} /></div><p className="muted">{item.category} · {item.quality_grade || "Standard grade"}</p><div className="split"><span>{item.quantity} {item.unit} available</span><span className="price">₹{Number(item.price_per_unit).toLocaleString("en-IN")}/{item.unit}</span></div><p className="muted">{item.location}</p><Link className="button" style={{width: "100%"}} to={`${prefix}/marketplace/${item.id}`}>View and order</Link></div></article>)}</div></StatePanel></>;
}

export function ProduceDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const state = useApiData(() => getMarketplaceProduce(id), [id]);
  const [quantity, setQuantity] = useState(1);
  const [review, setReview] = useState(null);
  const [relationships, setRelationships] = useState([]);
  const [relationshipId, setRelationshipId] = useState("");
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);
  const prefix = user.role === "BULK_BUYER" ? "/app/buyer" : "/app/consumer";

  async function reviewPurchase() {
    setWorking(true); setError("");
    try {
      const result = await reviewOrder({produce_id: Number(id), quantity: Number(quantity)});
      setReview(result);
      if (user.role === "BULK_BUYER") setRelationships(await listRelationships());
    } catch (err) { setError(err.message); }
    finally { setWorking(false); }
  }
  async function placeOrder() {
    setWorking(true); setError("");
    try { const payload = {produce_id: Number(id), quantity: Number(quantity)}; if (relationshipId) payload.relationship_id = Number(relationshipId); await createOrder(payload); navigate(`${prefix}/orders`); }
    catch (err) { setError(err.message); }
    finally { setWorking(false); }
  }

  return <><PageHeading eyebrow="Marketplace listing" title={state.data?.crop || "Produce detail"} description="Review the backend-authoritative price before placing the order." /><StatePanel loading={state.loading} error={state.error}>{state.data && <div className="dashboard-grid"><article className="card produce-card"><ProduceVisual item={state.data} /><div className="card-body"><div className="split"><h2>{state.data.crop}</h2><StatusBadge status={state.data.status} /></div><p>{state.data.category} · {state.data.quality_grade || "Standard grade"}</p><p className="price">₹{Number(state.data.price_per_unit).toLocaleString("en-IN")} per {state.data.unit}</p><p className="muted">{state.data.quantity} {state.data.unit} available · {state.data.location}</p></div></article><section className="card"><div className="card-header"><h2 className="section-heading">Order review</h2><ShoppingCart /></div><div className="card-body stack">{error && <div className="notice error">{error}</div>}<div className="field"><label htmlFor="order-quantity">Quantity ({state.data.unit})</label><input id="order-quantity" type="number" min="1" max={state.data.quantity} value={quantity} onChange={(e) => {setQuantity(e.target.value); setReview(null);}} /></div><button className="button secondary" onClick={reviewPurchase} disabled={working}>{working ? "Checking…" : "Review order"}</button>{review && <div className="notice"><div className="split"><span>Backend unit price</span><strong>₹{Number(review.unit_price).toLocaleString("en-IN")}</strong></div><div className="split" style={{marginTop: ".5rem"}}><span>Authoritative total</span><strong>₹{Number(review.total_amount).toLocaleString("en-IN")}</strong></div></div>}{review && user.role === "BULK_BUYER" && relationships.length > 0 && <div className="field"><label htmlFor="finance-relationship">Financing relationship (only if profile preference is PLATFORM)</label><select id="finance-relationship" value={relationshipId} onChange={(e) => setRelationshipId(e.target.value)}><option value="">No relationship</option>{relationships.filter((r) => r.status === "ACTIVE").map((r) => <option key={r.id} value={r.id}>Relationship #{r.id} · ₹{Number(r.credit_limit).toLocaleString("en-IN")}</option>)}</select></div>}{review && <button className="button" onClick={placeOrder} disabled={working}>{working ? "Placing order…" : "Place order"}</button>}</div></section></div>}</StatePanel></>;
}
