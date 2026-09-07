const STATES = ["PENDING", "ASSIGNED", "PICKED_UP", "IN_TRANSIT", "DELIVERED"];

export default function ShipmentTimeline({ status }) {
  const current = STATES.indexOf(status);
  return <div className="timeline" aria-label={`Shipment status: ${status}`}>{STATES.map((step, index) => <div className={`timeline-step ${current >= index ? "done" : ""}`} key={step}>{step.replaceAll("_", " ")}</div>)}</div>;
}
