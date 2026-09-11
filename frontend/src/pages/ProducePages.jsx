import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ImageOff, Pencil, Plus, Trash2 } from "lucide-react";
import { PageHeading, StatePanel, StatusBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { createProduce, deleteProduce, getProduce, listProduce, updateProduce } from "../api/produce";

export function ProduceListPage() {
  const { user } = useAuth();
  const state = useApiData(() => listProduce({farmer_id: user.id}), [user.id]);
  const [error, setError] = useState("");
  async function remove(id) {
    if (!window.confirm("Delete this produce listing? This cannot be undone.")) return;
    try { await deleteProduce(id); await state.reload(); }
    catch (err) { setError(err.message); }
  }
  return <><PageHeading eyebrow="Farmer inventory" title="My produce" description="Listings here are the single source used by the marketplace and order system." action={<Link className="button" to="/app/farmer/produce/new"><Plus size={17} />Add produce</Link>} />{error && <div className="notice error">{error}</div>}<section className="card"><StatePanel loading={state.loading} error={state.error} empty={!state.data?.length} emptyText="You have not listed any produce yet."><div className="table-wrap"><table><thead><tr><th>Crop</th><th>Category</th><th>Stock</th><th>Price</th><th>Location</th><th>Status</th><th>Actions</th></tr></thead><tbody>{state.data?.map((item) => <tr key={item.id}><td><strong>{item.crop}</strong></td><td>{item.category}</td><td>{item.quantity} {item.unit}</td><td>₹{Number(item.price_per_unit).toLocaleString("en-IN")}/{item.unit}</td><td>{item.location}</td><td><StatusBadge status={item.status} /></td><td><div className="actions"><Link className="button secondary small" to={`/app/farmer/produce/${item.id}/edit`}><Pencil size={15} />Edit</Link><button className="button danger small" onClick={() => remove(item.id)}><Trash2 size={15} /></button></div></td></tr>)}</tbody></table></div></StatePanel></section></>;
}

const blank = {crop: "", category: "", quantity: "", unit: "kg", price_per_unit: "", location: "", harvest_date: "", quality_grade: "", image: ""};

export function ProduceFormPage() {
  const { id } = useParams();
  const edit = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(blank);
  const [loading, setLoading] = useState(edit);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!edit) return;
    getProduce(id).then((item) => setForm({...blank, ...item, harvest_date: item.harvest_date || "", quality_grade: item.quality_grade || "", image: item.image || ""})).catch((err) => setError(err.message)).finally(() => setLoading(false));
  }, [edit, id]);

  async function submit(event) {
    event.preventDefault(); setSubmitting(true); setError("");
    const payload = {...form, quantity: Number(form.quantity), price_per_unit: Number(form.price_per_unit)};
    ["harvest_date", "quality_grade", "image", "status"].forEach((key) => { if (!payload[key]) delete payload[key]; });
    try { if (edit) await updateProduce(id, payload); else await createProduce(payload); navigate("/app/farmer/produce"); }
    catch (err) { setError(err.message); }
    finally { setSubmitting(false); }
  }

  function field(name, label, type = "text", props = {}) { return <div className="field"><label htmlFor={name}>{label}</label><input id={name} type={type} value={form[name]} onChange={(e) => setForm({...form, [name]: e.target.value})} required={props.required} min={props.min} /></div>; }
  return <><PageHeading eyebrow="Farmer inventory" title={edit ? "Edit produce" : "List new produce"} description="Marketplace price and stock come directly from this listing." /><section className="card"><div className="card-body"><StatePanel loading={loading} error={error && loading ? error : ""}>{error && <div className="notice error" style={{marginBottom: "1rem"}}>{error}</div>}<form onSubmit={submit} className="stack"><div className="form-grid">{field("crop", "Crop", "text", {required: true})}{field("category", "Category", "text", {required: true})}{field("quantity", "Available quantity", "number", {required: true, min: 0})}<div className="field"><label htmlFor="unit">Unit</label><select id="unit" value={form.unit} onChange={(e) => setForm({...form, unit: e.target.value})}><option>kg</option><option>quintal</option><option>ton</option><option>piece</option></select></div>{field("price_per_unit", "Price per unit (₹)", "number", {required: true, min: 0})}{field("location", "Location", "text", {required: true})}{field("harvest_date", "Harvest date", "date")}{field("quality_grade", "Quality grade")}{field("image", "Image URL")}{edit && <div className="field"><label htmlFor="status">Listing status</label><select id="status" value={form.status || "ACTIVE"} onChange={(e) => setForm({...form, status: e.target.value})}><option>ACTIVE</option><option>INACTIVE</option><option>SOLD_OUT</option></select></div>}</div><div className="form-actions"><button className="button" disabled={submitting}>{submitting ? "Saving…" : "Save listing"}</button><Link className="button secondary" to="/app/farmer/produce">Cancel</Link></div></form></StatePanel></div></section></>;
}

export function ProduceVisual({ item }) {
  return <div className="produce-image">{item.image ? <img src={item.image} alt={item.crop} /> : <ImageOff size={32} />}</div>;
}
