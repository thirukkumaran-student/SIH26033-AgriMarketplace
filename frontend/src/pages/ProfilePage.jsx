import { useEffect, useMemo, useState } from "react";
import { PageHeading, StatePanel } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { createProfile, getProfile, updateProfile } from "../api/profiles";

const fieldsByRole = {
  FARMER: [["phone","Phone"],["farm_name","Farm name"],["farm_size_acres","Farm size (acres)","number"],["farm_location","Farm location"],["soil_type","Soil type"],["irrigation_type","Irrigation type"],["bank_account_number","Bank account number"],["ifsc_code","IFSC code"]],
  CONSUMER: [["phone","Phone"],["address","Address"],["city","City"],["state","State"],["pincode","PIN code"]],
  BULK_BUYER: [["phone","Phone"],["address","Address"],["city","City"],["state","State"],["pincode","PIN code"],["financing_preference","Financing preference","select"]],
  FINANCIER: [["institution_name","Institution name"],["institution_type","Institution type"],["phone","Phone"],["address","Address"],["city","City"],["state","State"],["pincode","PIN code"]],
};

export default function ProfilePage() {
  const { user } = useAuth();
  const fields = useMemo(() => fieldsByRole[user.role] || [], [user.role]);
  const [form, setForm] = useState({});
  const [exists, setExists] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [working, setWorking] = useState(false);

  useEffect(() => { getProfile(user.role).then((data) => {setForm(data); setExists(true);}).catch((err) => { if (err.status !== 404) setError(err.message); }).finally(() => setLoading(false)); }, [user.role]);
  async function submit(event) { event.preventDefault(); setWorking(true); setError(""); setSuccess(""); const payload = {}; fields.forEach(([name,,type]) => { if (form[name] !== undefined && form[name] !== "") payload[name] = type === "number" ? Number(form[name]) : form[name]; }); try { const saved = exists ? await updateProfile(user.role,payload) : await createProfile(user.role,payload); setForm(saved); setExists(true); setSuccess("Profile saved."); } catch(err) {setError(err.message);} finally {setWorking(false);} }
  return <><PageHeading eyebrow="Account details" title="Profile" description="Identity and role come from the authenticated backend user; these fields store role-specific details." /><section className="card"><div className="card-body"><StatePanel loading={loading} error={loading ? error : ""}>{error && <div className="notice error" style={{marginBottom:"1rem"}}>{error}</div>}{success && <div className="notice" style={{marginBottom:"1rem"}}>{success}</div>}<form className="stack" onSubmit={submit}><div className="form-grid">{fields.map(([name,label,type="text"]) => <div className="field" key={name}><label htmlFor={`profile-${name}`}>{label}</label>{type === "select" ? <select id={`profile-${name}`} value={form[name] || "NONE"} onChange={(e) => setForm({...form,[name]:e.target.value})}><option value="NONE">No platform financing</option><option value="PLATFORM">Platform financing</option></select> : <input id={`profile-${name}`} type={type} min={type === "number" ? 0 : undefined} value={form[name] || ""} onChange={(e) => setForm({...form,[name]:e.target.value})} required={name === "institution_name"} />}</div>)}</div><button className="button" disabled={working}>{working ? "Saving…" : exists ? "Update profile" : "Create profile"}</button></form></StatePanel></div></section></>;
}
