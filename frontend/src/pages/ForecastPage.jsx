import { useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageHeading, StatePanel } from "../components/ui";
import useApiData from "../hooks/useApiData";
import { getSuggestion, listForecasts, predictForecast } from "../api/forecast";

export default function ForecastPage() {
  const history = useApiData(listForecasts, []);
  const [form, setForm] = useState({crop: "Tomato", district_name: "Chennai", date: new Date().toISOString().slice(0,10), lag_1: "100", lag_2: "90", days_since_previous: "7", available_quantity: "80"});
  const [result, setResult] = useState(null);
  const [suggestion, setSuggestion] = useState(null);
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);

  async function submit(event) {
    event.preventDefault(); setWorking(true); setError("");
    const forecastPayload = {crop: form.crop, district_name: form.district_name, date: form.date, lag_1: Number(form.lag_1), lag_2: Number(form.lag_2), days_since_previous: Number(form.days_since_previous)};
    try { const [forecast, advice] = await Promise.all([predictForecast(forecastPayload), getSuggestion({...forecastPayload, available_quantity: Number(form.available_quantity)})]); setResult(forecast); setSuggestion(advice); await history.reload(); }
    catch (err) { setError(err.message); }
    finally { setWorking(false); }
  }
  const numericFields = [["lag_1", "Previous activity (lag 1)"], ["lag_2", "Previous activity (lag 2)"], ["days_since_previous", "Days since prior observation"], ["available_quantity", "Available quantity"]];
  return <><PageHeading eyebrow="Decision support" title="Market activity forecast" description="The model estimates an activity/arrival quantity proxy. It is not a guarantee of consumer demand." /><div className="dashboard-grid"><section className="card"><div className="card-header"><h2 className="section-heading">Generate forecast</h2></div><div className="card-body">{error && <div className="notice error" style={{marginBottom: "1rem"}}>{error}</div>}<form className="stack" onSubmit={submit}><div className="form-grid"><div className="field"><label htmlFor="forecast-crop">Crop</label><input id="forecast-crop" value={form.crop} onChange={(e) => setForm({...form, crop:e.target.value})} required /></div><div className="field"><label htmlFor="forecast-district">District</label><input id="forecast-district" value={form.district_name} onChange={(e) => setForm({...form, district_name:e.target.value})} required /></div><div className="field"><label htmlFor="forecast-date">Forecast date</label><input id="forecast-date" type="date" value={form.date} onChange={(e) => setForm({...form, date:e.target.value})} required /></div>{numericFields.map(([name,label]) => <div className="field" key={name}><label htmlFor={`forecast-${name}`}>{label}</label><input id={`forecast-${name}`} type="number" min="0" value={form[name]} onChange={(e) => setForm({...form, [name]:e.target.value})} required /></div>)}</div><button className="button" disabled={working}>{working ? "Calculating…" : "Generate decision support"}</button></form>{result && <div className="notice" style={{marginTop:"1rem"}}><strong>{result.crop}: {Math.round(result.predicted_demand).toLocaleString("en-IN")}</strong><div>Activity quantity proxy for {result.district_name} on {result.date}.</div></div>}{suggestion && <div className="notice warning" style={{marginTop:".75rem"}}><strong>{suggestion.suggestion}</strong><div>{suggestion.reason}</div></div>}</div></section><section className="card"><div className="card-header"><h2 className="section-heading">Forecast history</h2></div><div className="card-body"><StatePanel loading={history.loading} error={history.error} empty={!history.data?.length} emptyText="No forecasts recorded yet.">{history.data?.length > 0 && <div style={{height: 260}}><ResponsiveContainer width="100%" height="100%"><LineChart data={[...history.data].reverse().slice(-12)}><CartesianGrid strokeDasharray="3 3" stroke="#e4e9e4" /><XAxis dataKey="date" tick={{fontSize: 11}} /><YAxis tick={{fontSize: 11}} /><Tooltip /><Line dataKey="predicted_demand" stroke="#208347" strokeWidth={3} /></LineChart></ResponsiveContainer></div>}</StatePanel></div></section></div></>;
}
