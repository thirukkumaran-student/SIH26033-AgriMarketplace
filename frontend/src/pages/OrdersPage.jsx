import { useState } from "react";
import { PageHeading, StatePanel, StatusBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { listOrders, simulateOrderPayment, updateOrderStatus } from "../api/orders";

const PAYMENT_METHODS = [
  ["UPI", "UPI"],
  ["CARD", "Card"],
  ["BANK_TRANSFER", "Bank transfer"],
  ["CASH", "Cash"],
];

function PaymentSummary({ order }) {
  return <div className="payment-summary">
    <StatusBadge status={order.payment_status} />
    {order.payment_status === "PAID" && <small className="muted">
      {order.payment_method?.replaceAll("_", " ")} · {order.payment_reference}
    </small>}
  </div>;
}

export default function OrdersPage() {
  const { user } = useAuth();
  const state = useApiData(listOrders, []);
  const [actionError, setActionError] = useState("");
  const [working, setWorking] = useState(null);
  const [paymentOrder, setPaymentOrder] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState("UPI");

  const isBuyer = user.role === "CONSUMER" || user.role === "BULK_BUYER";
  const cashUnavailable = Number(paymentOrder?.total_amount || 0) >= 500;

  function nextActions(order) {
    if (isBuyer && order.status === "PENDING") return [["Cancel", "CANCELLED"]];
    if ((user.role === "FARMER" || user.role === "ADMIN") && order.status === "PENDING") return [["Confirm", "CONFIRMED"]];
    if ((user.role === "FARMER" || user.role === "ADMIN") && order.status === "CONFIRMED") return [["Complete", "COMPLETED"]];
    return [];
  }

  function canPay(order) {
    return isBuyer
      && order.payment_status === "UNPAID"
      && ["PENDING", "CONFIRMED"].includes(order.status);
  }

  async function transition(order, status) {
    setWorking(order.id);
    setActionError("");
    try {
      await updateOrderStatus(order.id, status);
      await state.reload();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setWorking(null);
    }
  }

  function openPayment(order) {
    setPaymentOrder(order);
    setPaymentMethod("UPI");
    setActionError("");
  }

  async function payFarmer(event) {
    event.preventDefault();
    setWorking(paymentOrder.id);
    setActionError("");
    try {
      await simulateOrderPayment(paymentOrder.id, paymentMethod);
      setPaymentOrder(null);
      await state.reload();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setWorking(null);
    }
  }

  return <>
    <PageHeading
      eyebrow="Shared order system"
      title="Orders"
      description="Order status and produce payment status are tracked separately. Payments shown here are simulations."
    />
    {actionError && <div className="notice error" style={{ marginBottom: "1rem" }}>{actionError}</div>}
    <section className="card">
      <StatePanel loading={state.loading} error={state.error} empty={!state.data?.length} emptyText="No orders are available for this account.">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Order</th><th>Produce</th><th>Quantity</th><th>Total</th><th>Order status</th><th>Produce payment</th><th>Action</th></tr></thead>
            <tbody>{state.data?.map((order) => <tr key={order.id}>
              <td>#{order.id}</td>
              <td>#{order.produce_id}<div className="muted">₹{Number(order.unit_price).toLocaleString("en-IN")} each</div></td>
              <td>{order.quantity}</td>
              <td><strong>₹{Number(order.total_amount).toLocaleString("en-IN")}</strong></td>
              <td><StatusBadge status={order.status} /></td>
              <td><PaymentSummary order={order} /></td>
              <td><div className="actions">
                {canPay(order) && <button className="button small" disabled={working === order.id} onClick={() => openPayment(order)}>Pay farmer</button>}
                {nextActions(order).map(([label, status]) => <button key={status} disabled={working === order.id} className={`button small ${status === "CANCELLED" ? "danger" : ""}`} onClick={() => transition(order, status)}>{working === order.id ? "Working…" : label}</button>)}
              </div></td>
            </tr>)}</tbody>
          </table>
        </div>
      </StatePanel>
    </section>

    {paymentOrder && <div className="modal-backdrop" role="presentation">
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="payment-title">
        <div className="card-header">
          <div><p className="eyebrow">Demo Payment Simulation</p><h2 id="payment-title">Pay farmer</h2></div>
          <button className="button ghost small" onClick={() => setPaymentOrder(null)}>Close</button>
        </div>
        <div className="card-body">
          <div className="payment-review">
            <div><small className="muted">Order</small><strong>#{paymentOrder.id}</strong></div>
            <div><small className="muted">Produce amount</small><strong>₹{Number(paymentOrder.total_amount).toLocaleString("en-IN")}</strong></div>
            <div><small className="muted">Recipient</small><strong>Farmer</strong></div>
          </div>
          <form className="stack" onSubmit={payFarmer}>
            <div className="field">
              <label htmlFor="payment-method">Payment method</label>
              <select id="payment-method" value={paymentMethod} onChange={(event) => setPaymentMethod(event.target.value)}>
                {PAYMENT_METHODS.map(([value, label]) => <option key={value} value={value} disabled={value === "CASH" && cashUnavailable}>{label}{value === "CASH" && cashUnavailable ? " — unavailable for ₹500 or more" : ""}</option>)}
              </select>
            </div>
            {cashUnavailable && <div className="notice warning">Cash is available only when the order total is strictly below ₹500. Choose UPI, card, or bank transfer.</div>}
            <div className="notice"><strong>Demo only — no real money is transferred.</strong><br />No PIN, OTP, card details, or bank credentials are requested.</div>
            <button className="button" disabled={working === paymentOrder.id}>{working === paymentOrder.id ? "Simulating…" : "Simulate payment"}</button>
          </form>
        </div>
      </section>
    </div>}
  </>;
}
