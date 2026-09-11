import { useState } from "react";
import { PageHeading, StatePanel, StatusBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { listOrders, updateOrderStatus } from "../api/orders";

export default function OrdersPage() {
  const { user } = useAuth();
  const state = useApiData(listOrders, []);
  const [actionError, setActionError] = useState("");
  const [working, setWorking] = useState(null);

  function nextActions(order) {
    if ((user.role === "CONSUMER" || user.role === "BULK_BUYER") && order.status === "PENDING") return [["Cancel", "CANCELLED"]];
    if ((user.role === "FARMER" || user.role === "ADMIN") && order.status === "PENDING") return [["Confirm", "CONFIRMED"]];
    if ((user.role === "FARMER" || user.role === "ADMIN") && order.status === "CONFIRMED") return [["Complete", "COMPLETED"]];
    return [];
  }

  async function transition(order, status) {
    setWorking(order.id); setActionError("");
    try { await updateOrderStatus(order.id, status); await state.reload(); }
    catch (err) { setActionError(err.message); }
    finally { setWorking(null); }
  }

  return <><PageHeading eyebrow="Shared order system" title="Orders" description="Totals, ownership, stock, and state transitions are enforced by the backend." />{actionError && <div className="notice error" style={{marginBottom: "1rem"}}>{actionError}</div>}<section className="card"><StatePanel loading={state.loading} error={state.error} empty={!state.data?.length} emptyText="No orders are available for this account."><div className="table-wrap"><table><thead><tr><th>Order</th><th>Produce</th><th>Quantity</th><th>Unit price</th><th>Total</th><th>Status</th><th>Action</th></tr></thead><tbody>{state.data?.map((order) => <tr key={order.id}><td>#{order.id}</td><td>#{order.produce_id}</td><td>{order.quantity}</td><td>₹{Number(order.unit_price).toLocaleString("en-IN")}</td><td><strong>₹{Number(order.total_amount).toLocaleString("en-IN")}</strong></td><td><StatusBadge status={order.status} /></td><td><div className="actions">{nextActions(order).map(([label, status]) => <button key={status} disabled={working === order.id} className={`button small ${status === "CANCELLED" ? "danger" : ""}`} onClick={() => transition(order, status)}>{working === order.id ? "Working…" : label}</button>)}</div></td></tr>)}</tbody></table></div></StatePanel></section></>;
}
