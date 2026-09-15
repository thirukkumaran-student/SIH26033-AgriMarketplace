import { PageHeading, StatePanel, StatusBadge } from "../components/ui";
import ShipmentTimeline from "../components/ShipmentTimeline";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { listConsumerShipments, listFarmerShipments } from "../api/shipments";

export default function ShipmentsPage() {
  const { user } = useAuth();
  const state = useApiData(user.role === "FARMER" ? listFarmerShipments : listConsumerShipments, [user.role]);

  return <>
    <PageHeading eyebrow="Supply-chain tracking" title="Shipments" description="Shipment progress and logistics-fee collection remain separate states." />
    <StatePanel loading={state.loading} error={state.error} empty={!state.data?.length} emptyText="No shipments are linked to your orders yet.">
      <div className="stack">{state.data?.map((shipment) => <article className="card" key={shipment.id}>
        <div className="card-header">
          <div><h2 className="section-heading">Shipment #{shipment.id}</h2><p className="muted">Order #{shipment.order_id} · {shipment.crop}</p></div>
          <StatusBadge status={shipment.status} />
        </div>
        <div className="card-body">
          <ShipmentTimeline status={shipment.status} />
          <div className="form-grid">
            <div><small className="muted">Pickup</small><div>{shipment.pickup_location}</div></div>
            <div><small className="muted">Destination</small><div>{shipment.destination}</div></div>
            <div><small className="muted">Estimated delivery</small><div>{shipment.estimated_delivery ? new Date(shipment.estimated_delivery).toLocaleString() : "Not set"}</div></div>
            <div><small className="muted">Logistics cost</small><div>₹{Number(shipment.logistics_cost).toLocaleString("en-IN")}</div></div>
          </div>
          {user.role === "FARMER" && <div className="fee-panel">
            <div><small className="muted">Payer</small><strong>Farmer</strong></div>
            <div><small className="muted">Recipient</small><strong>Logistics operator</strong></div>
            <div><small className="muted">Logistics fee</small><StatusBadge status={shipment.logistics_fee_status} /></div>
            {shipment.logistics_fee_reference && <div><small className="muted">Reference</small><strong>{shipment.logistics_fee_reference}</strong></div>}
          </div>}
        </div>
      </article>)}</div>
    </StatePanel>
  </>;
}
