import { PageHeading, StatePanel, StatusBadge } from "../components/ui";
import ShipmentTimeline from "../components/ShipmentTimeline";
import { useAuth } from "../context/AuthContext";
import useApiData from "../hooks/useApiData";
import { listConsumerShipments, listFarmerShipments } from "../api/shipments";

export default function ShipmentsPage() {
  const { user } = useAuth();
  const state = useApiData(user.role === "FARMER" ? listFarmerShipments : listConsumerShipments, [user.role]);
  return <><PageHeading eyebrow="Supply-chain tracking" title="Shipments" description="Shipment progress reflects the existing backend lifecycle; live GPS is not available." /><StatePanel loading={state.loading} error={state.error} empty={!state.data?.length} emptyText="No shipments are linked to your orders yet."><div className="stack">{state.data?.map((shipment) => <article className="card" key={shipment.id}><div className="card-header"><div><h2 className="section-heading">Shipment #{shipment.id}</h2><p className="muted">Order #{shipment.order_id} · {shipment.crop}</p></div><StatusBadge status={shipment.status} /></div><div className="card-body"><ShipmentTimeline status={shipment.status} /><div className="form-grid"><div><small className="muted">Pickup</small><div>{shipment.pickup_location}</div></div><div><small className="muted">Destination</small><div>{shipment.destination}</div></div><div><small className="muted">Estimated delivery</small><div>{shipment.estimated_delivery ? new Date(shipment.estimated_delivery).toLocaleString() : "Not set"}</div></div><div><small className="muted">Logistics cost</small><div>₹{Number(shipment.logistics_cost).toLocaleString("en-IN")}</div></div></div></div></article>)}</div></StatePanel></>;
}
