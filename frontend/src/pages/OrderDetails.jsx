import { useParams, useNavigate } from 'react-router'
import { StatusPill } from './Dashboard'
import { ArrowLeft, Mail, Phone, MapPin, CheckCircle } from 'lucide-react'
import { ORDERS_LIST, ORDER_STATUS_VARIANT, PRODUCE_IMAGES, DEFAULT_IMG, formatPrice } from '../data'
import { GreenBtn, OutlineBtn } from './Dashboard'

const STEPS = [
  { key: 'Placed',      label: 'Placed'      },
  { key: 'Processing',  label: 'Processing'  },
  { key: 'Shipped',     label: 'Shipped'     },
  { key: 'Delivered',   label: 'Delivered'   },
]

function stepIndex(status) {
  const map = { Pending: 0, Processing: 1, Shipped: 2, Delivered: 3, Cancelled: -1 }
  return map[status] ?? 0
}

export default function OrderDetails() {
  const { id }   = useParams()
  const navigate = useNavigate()
  const order    = ORDERS_LIST.find(o => o.id === id)

  if (!order) return (
    <div style={{ padding: 24 }}>
      <BackBtn onClick={() => navigate('/orders')} />
      <p style={{ fontFamily: 'var(--agri-font)', color: 'var(--agri-text-secondary)', marginTop: 20 }}>Order not found.</p>
    </div>
  )

  const activeStep = stepIndex(order.status)

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <BackBtn onClick={() => navigate('/orders')} label="Back to Orders" />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>
          Order #{order.id}
        </h1>
        <StatusPill status={order.status} variant={ORDER_STATUS_VARIANT[order.status]} />
        <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', marginLeft: 4 }}>
          Placed on {order.date}, {order.placedTime}
        </span>
      </div>

      {/* 3-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>

        {/* Col 1: Product Details */}
        <DetailCard title="Product Details">
          <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
            <img src={PRODUCE_IMAGES[order.product] || DEFAULT_IMG} alt={order.product}
              style={{ width: 80, height: 80, borderRadius: 10, objectFit: 'cover', flexShrink: 0 }} />
            <div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: 'var(--agri-text)', marginBottom: 5 }}>{order.product}</div>
              <InfoLine label="Quantity"     value={`${order.qty} ${order.unit}`} />
              <InfoLine label="Price per Unit" value={`₹${order.total / order.qty}/${order.unit}`} />
              <InfoLine label="Total Amount"   value={<strong>{formatPrice(order.total)}</strong>} />
            </div>
          </div>
        </DetailCard>

        {/* Col 2: Buyer + Shipping */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <DetailCard title="Buyer Information">
            <BuyerRow icon={<Mail size={13} color="var(--agri-text-muted)" />} text={order.buyer} bold />
            <BuyerRow icon={<Mail size={13} color="var(--agri-text-muted)" />} text={order.buyerEmail} />
            <BuyerRow icon={<Phone size={13} color="var(--agri-text-muted)" />} text={order.buyerPhone} />
            <BuyerRow icon={<MapPin size={13} color="var(--agri-text-muted)" />} text={order.buyerAddress} />
          </DetailCard>
          <DetailCard title="Shipping Information">
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, color: 'var(--agri-text-secondary)', marginBottom: 10 }}>
              {order.status === 'Shipped' || order.status === 'Delivered' ? 'Shipment dispatched' : 'To be assigned'}
            </div>
            <button onClick={() => navigate('/shipments')}
              style={{ width: '100%', padding: '9px', background: 'white', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 500, color: 'var(--agri-text)', cursor: 'pointer' }}>
              Update Shipment
            </button>
          </DetailCard>
        </div>

        {/* Col 3: Order Timeline */}
        <DetailCard title="Order Timeline">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {STEPS.map((step, i) => {
              const done    = i <= activeStep
              const current = i === activeStep
              return (
                <div key={step.key} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{ width: 22, height: 22, borderRadius: '50%', background: done ? 'var(--agri-primary)' : '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      {done ? <CheckCircle size={13} color="white" /> : <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#9CA3AF', display: 'block' }} />}
                    </div>
                    {i < STEPS.length - 1 && (
                      <div style={{ width: 2, height: 24, background: done && i < activeStep ? 'var(--agri-primary)' : '#e5e7eb', margin: '2px 0' }} />
                    )}
                  </div>
                  <div style={{ paddingBottom: 8 }}>
                    <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: current ? 600 : 400, color: done ? 'var(--agri-text)' : 'var(--agri-text-muted)' }}>
                      {step.label}
                    </div>
                    <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)' }}>
                      {i === 0 ? `${order.date}, ${order.placedTime}`
                        : i === 1 && order.status !== 'Pending' ? `${order.date}, ${order.processedTime}`
                        : '—'}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </DetailCard>
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: 10 }}>
        {order.status === 'Processing' && (
          <GreenBtn onClick={() => navigate('/shipments')}>Mark as Shipped</GreenBtn>
        )}
        {order.status === 'Pending' && (
          <GreenBtn onClick={() => {}}>Accept Order</GreenBtn>
        )}
        {(order.status === 'Pending' || order.status === 'Processing') && (
          <OutlineBtn danger onClick={() => {}}>Cancel Order</OutlineBtn>
        )}
        <OutlineBtn onClick={() => navigate('/orders')}>Back to Orders</OutlineBtn>
      </div>
    </div>
  )
}

function BackBtn({ onClick, label = 'Back' }) {
  return (
    <button onClick={onClick} style={{ display: 'flex', alignItems: 'center', gap: 5, background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 16, color: 'var(--agri-primary)', padding: 0, fontWeight: 500 }}>
      <ArrowLeft size={14} /> {label}
    </button>
  )
}
function DetailCard({ title, children }) {
  return (
    <div style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
      <div style={{ padding: '11px 14px', borderBottom: '1px solid var(--agri-border)' }}>
        <span style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: 'var(--agri-text)' }}>{title}</span>
      </div>
      <div style={{ padding: 14 }}>{children}</div>
    </div>
  )
}
function InfoLine({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)' }}>{label}</span>
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)' }}>{value}</span>
    </div>
  )
}
function BuyerRow({ icon, text, bold }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 6 }}>
      {icon}
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 16, color: bold ? 'var(--agri-text)' : 'var(--agri-text-secondary)', fontWeight: bold ? 600 : 400 }}>{text}</span>
    </div>
  )
}
