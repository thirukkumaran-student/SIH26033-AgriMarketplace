import { Link } from "react-router-dom";
import { BadgeCheck, Boxes, CircleDollarSign, ClipboardClock, ClipboardList, Gauge, Handshake, PackageCheck, Scale, ShieldCheck, ShoppingBasket, Sprout, Truck } from "lucide-react";
import MarketPricePanel from "../components/MarketPricePanel";
import { MetricCard, PageHeading, StatePanel, StatusBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { listProduce } from "../api/produce";
import { listOrders } from "../api/orders";
import { listFarmerShipments, listConsumerShipments } from "../api/shipments";
import { listForecasts } from "../api/forecast";
import { listMarketplace } from "../api/marketplace";
import { listRelationships, listFinanceRequests } from "../api/finance";
import { listLogisticsShipments } from "../api/logistics";
import { getMonitoring, listDisputes, listVerifications } from "../api/admin";

function OrdersTable({ orders, limit = 5 }) {
  if (!orders?.length) return <div className="state-panel"><p>No orders yet.</p></div>;
  return <div className="table-wrap"><table><thead><tr><th>Order</th><th>Produce</th><th>Quantity</th><th>Total</th><th>Status</th></tr></thead><tbody>{orders.slice(0, limit).map((order) => <tr key={order.id}><td>#{order.id}</td><td>#{order.produce_id}</td><td>{order.quantity}</td><td>₹{Number(order.total_amount).toLocaleString("en-IN")}</td><td><StatusBadge status={order.status} /></td></tr>)}</tbody></table></div>;
}

export function FarmerDashboard() {
  const { user } = useAuth();
  const state = useApiData(async () => {
    const [produce, orders, shipments, forecasts] = await Promise.all([listProduce({farmer_id: user.id}), listOrders(), listFarmerShipments(), listForecasts()]);
    return { produce, orders, shipments, forecasts };
  }, [user.id]);
  const data = state.data || {produce: [], orders: [], shipments: [], forecasts: []};
  return <><PageHeading eyebrow="Farmer dashboard" title={`Namaste, ${user.name}`} description="Your listings, buyer orders, market reference, and forecast signals in one place." action={<Link className="button" to="/app/farmer/produce/new">List produce</Link>} />
    <StatePanel loading={state.loading} error={state.error}>
      <div className="metrics-grid"><MetricCard label="Active listings" value={data.produce.filter((p) => p.status === "ACTIVE").length} icon={Sprout} /><MetricCard label="Pending orders" value={data.orders.filter((o) => o.status === "PENDING").length} icon={ClipboardClock} /><MetricCard label="Total orders" value={data.orders.length} icon={ClipboardList} /><MetricCard label="Shipments" value={data.shipments.length} icon={Truck} /></div>
      <div className="dashboard-grid"><div className="stack"><section className="card"><div className="card-header"><h2 className="section-heading">Recent orders</h2><Link className="muted" to="/app/farmer/orders">View all</Link></div><OrdersTable orders={data.orders} /></section><MarketPricePanel listings={data.produce} /></div><div className="stack"><section className="card"><div className="card-header"><h2 className="section-heading">Inventory snapshot</h2></div><div className="card-body">{data.produce.length ? data.produce.slice(0, 5).map((item) => <div className="split" key={item.id} style={{padding: ".65rem 0", borderBottom: "1px solid var(--line)"}}><div><strong>{item.crop}</strong><div className="muted">{item.quantity} {item.unit}</div></div><StatusBadge status={item.status} /></div>) : <p className="muted">No produce listed yet.</p>}</div></section><section className="card"><div className="card-header"><h2 className="section-heading">Market activity forecast</h2><Link className="muted" to="/app/farmer/forecast">Open</Link></div><div className="card-body">{data.forecasts[0] ? <><strong>{data.forecasts[0].crop}</strong><div className="metric-value">{Math.round(data.forecasts[0].predicted_demand).toLocaleString("en-IN")}</div><p className="muted">Activity quantity proxy for {data.forecasts[0].district_name} on {data.forecasts[0].date}. This is decision support, not guaranteed consumer demand.</p></> : <p className="muted">No forecast has been generated yet.</p>}</div></section></div></div>
    </StatePanel></>;
}

export function ConsumerDashboard() {
  const { user } = useAuth();
  const state = useApiData(async () => { const [market, orders, shipments] = await Promise.all([listMarketplace(), listOrders(), listConsumerShipments()]); return {market, orders, shipments}; }, []);
  const data = state.data || {market: [], orders: [], shipments: []};
  return <><PageHeading eyebrow="Consumer dashboard" title={`Welcome, ${user.name}`} description="Find verified produce, place an order, and follow delivery progress." action={<Link className="button" to="/app/consumer/marketplace">Browse marketplace</Link>} /><StatePanel loading={state.loading} error={state.error}><div className="metrics-grid"><MetricCard label="Available produce" value={data.market.length} icon={ShoppingBasket} /><MetricCard label="Your orders" value={data.orders.length} icon={ClipboardList} /><MetricCard label="Active shipments" value={data.shipments.filter((s) => s.status !== "DELIVERED" && s.status !== "CANCELLED").length} icon={Truck} /><MetricCard label="Delivered" value={data.shipments.filter((s) => s.status === "DELIVERED").length} icon={PackageCheck} /></div><div className="dashboard-grid"><section className="card"><div className="card-header"><h2 className="section-heading">Recent orders</h2><Link className="muted" to="/app/consumer/orders">View all</Link></div><OrdersTable orders={data.orders} /></section><section className="card"><div className="card-header"><h2 className="section-heading">Fresh from verified farms</h2></div><div className="card-body">{data.market.slice(0,4).map((item) => <div className="split" key={item.id} style={{padding: ".65rem 0", borderBottom: "1px solid var(--line)"}}><div><strong>{item.crop}</strong><div className="muted">{item.location}</div></div><span className="price">₹{item.price_per_unit}/{item.unit}</span></div>)}{!data.market.length && <p className="muted">No marketplace listings are available.</p>}</div></section></div></StatePanel></>;
}

export function BuyerDashboard() {
  const { user } = useAuth();
  const state = useApiData(async () => { const [market, orders, relationships, requests] = await Promise.all([listMarketplace(), listOrders(), listRelationships(), listFinanceRequests()]); return {market, orders, relationships, requests}; }, []);
  const data = state.data || {market: [], orders: [], relationships: [], requests: []};
  return <><PageHeading eyebrow="Bulk procurement" title={`Welcome, ${user.name}`} description="Manage wholesale orders and financing through the shared marketplace." action={<Link className="button" to="/app/buyer/marketplace">Source produce</Link>} /><StatePanel loading={state.loading} error={state.error}><div className="metrics-grid"><MetricCard label="Available listings" value={data.market.length} icon={Boxes} /><MetricCard label="Orders" value={data.orders.length} icon={ClipboardList} /><MetricCard label="Active finance" value={data.relationships.filter((r) => r.status === "ACTIVE").length} icon={CircleDollarSign} /><MetricCard label="Pending finance" value={data.requests.filter((r) => r.status === "PENDING").length} icon={ClipboardClock} /></div><div className="dashboard-grid"><section className="card"><div className="card-header"><h2 className="section-heading">Recent procurement</h2></div><OrdersTable orders={data.orders} /></section><section className="card"><div className="card-header"><h2 className="section-heading">Shipment visibility</h2></div><div className="card-body"><div className="notice warning">Bulk-buyer shipment tracking is not exposed by the current backend. Order status remains available here without inventing shipment data.</div></div></section></div></StatePanel></>;
}

export function FinancierDashboard() {
  const { user } = useAuth();
  const state = useApiData(async () => { const [relationships, requests] = await Promise.all([listRelationships(), listFinanceRequests()]); return {relationships, requests}; }, []);
  const data = state.data || {relationships: [], requests: []};
  return <><PageHeading eyebrow="Financier dashboard" title={`Welcome, ${user.name}`} description="Review incoming financing requests and active buyer relationships." /><StatePanel loading={state.loading} error={state.error}><div className="metrics-grid"><MetricCard label="Pending requests" value={data.requests.filter((r) => r.status === "PENDING").length} icon={ClipboardClock} /><MetricCard label="Approved offers" value={data.requests.filter((r) => r.status === "APPROVED").length} icon={BadgeCheck} /><MetricCard label="Active relationships" value={data.relationships.filter((r) => r.status === "ACTIVE").length} icon={Handshake} /></div><section className="card"><div className="card-header"><h2 className="section-heading">Latest requests</h2><Link className="muted" to="/app/financier/requests">Manage</Link></div><div className="table-wrap"><table><thead><tr><th>Request</th><th>Buyer</th><th>Credit offer</th><th>Status</th></tr></thead><tbody>{data.requests.slice(0,6).map((item) => <tr key={item.id}><td>#{item.id}</td><td>#{item.buyer_id}</td><td>₹{Number(item.credit_limit).toLocaleString("en-IN")}</td><td><StatusBadge status={item.status} /></td></tr>)}</tbody></table></div></section></StatePanel></>;
}

export function LogisticsDashboard() {
  const { user } = useAuth();
  const state = useApiData(listLogisticsShipments, []);
  const shipments = state.data || [];
  return <><PageHeading eyebrow="Logistics operations" title={`Welcome, ${user.name}`} description="Move shared shipments through the supported operational lifecycle." action={<Link className="button" to="/app/logistics/shipments">Manage shipments</Link>} /><StatePanel loading={state.loading} error={state.error}><div className="metrics-grid"><MetricCard label="Pending" value={shipments.filter((s) => s.status === "PENDING").length} icon={ClipboardClock} /><MetricCard label="Assigned" value={shipments.filter((s) => s.status === "ASSIGNED").length} icon={Truck} /><MetricCard label="In transit" value={shipments.filter((s) => s.status === "IN_TRANSIT").length} icon={Truck} /><MetricCard label="Delivered" value={shipments.filter((s) => s.status === "DELIVERED").length} icon={PackageCheck} /></div><section className="card"><div className="card-header"><h2 className="section-heading">Current shipments</h2></div><div className="table-wrap"><table><thead><tr><th>Shipment</th><th>Order</th><th>Route</th><th>Status</th></tr></thead><tbody>{shipments.slice(0,8).map((item) => <tr key={item.id}><td><Link to={`/app/logistics/shipments/${item.id}`}>#{item.id}</Link></td><td>#{item.order_id}</td><td>{item.pickup_location} → {item.destination}</td><td><StatusBadge status={item.status} /></td></tr>)}</tbody></table></div></section></StatePanel></>;
}

export function AdminDashboard() {
  const { user } = useAuth();
  const state = useApiData(async () => { const [verifications, disputes, monitoring, orders] = await Promise.all([listVerifications(), listDisputes(), getMonitoring(), listOrders()]); return {verifications, disputes, monitoring, orders}; }, []);
  const data = state.data || {verifications: [], disputes: [], orders: [], monitoring: null};
  return <><PageHeading eyebrow="Admin operations" title={`Welcome, ${user.name}`} description="Focus on verification, disputes, and service health without fabricated analytics." /><StatePanel loading={state.loading} error={state.error}><div className="metrics-grid"><MetricCard label="Pending verification" value={data.verifications.filter((v) => v.overall_status === "PENDING").length} icon={ShieldCheck} /><MetricCard label="Open disputes" value={data.disputes.filter((d) => d.status === "OPEN").length} icon={Scale} /><MetricCard label="Orders" value={data.orders.length} icon={ClipboardList} /><MetricCard label="System status" value={data.monitoring?.status || "—"} icon={Gauge} /></div><div className="dashboard-grid"><section className="card"><div className="card-header"><h2 className="section-heading">Verification queue</h2><Link className="muted" to="/app/admin/verifications">Review</Link></div><div className="table-wrap"><table><thead><tr><th>Applicant</th><th>Documents</th><th>Status</th></tr></thead><tbody>{data.verifications.slice(0,6).map((item) => <tr key={item.user_id}><td>{item.applicant_name}</td><td>{item.document_count}</td><td><StatusBadge status={item.overall_status} /></td></tr>)}</tbody></table></div></section><section className="card"><div className="card-header"><h2 className="section-heading">Monitoring</h2></div><div className="card-body"><div className="split"><span>Application</span><StatusBadge status={data.monitoring?.status} /></div><div className="split" style={{marginTop: "1rem"}}><span>Database</span><StatusBadge status={data.monitoring?.database?.status} /></div></div></section></div></StatePanel></>;
}
