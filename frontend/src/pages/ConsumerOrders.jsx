import { useState } from 'react'
import { useNavigate } from 'react-router'
import { CONSUMER_ORDERS } from '../data/consumerData'

const TABS = ['All Orders', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

function StatusPill({ status }) {
  const map = {
    Delivered: { bg: '#dcfce7', color: '#16a34a' },
    Shipped: { bg: '#dbeafe', color: '#2563eb' },
    Processing: { bg: '#fef3c7', color: '#d97706' },
    Cancelled: { bg: '#fee2e2', color: '#dc2626' },
  }
  const s = map[status] || { bg: '#f3f4f6', color: '#6b7280' }
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 12px', borderRadius: 20 }}>{status}</span>
}

export default function ConsumerOrders() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('All Orders')

  const filtered = tab === 'All Orders' ? CONSUMER_ORDERS : CONSUMER_ORDERS.filter(o => o.status === tab)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, padding: '24px 32px' }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>My Orders</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Track and manage your orders.</p>
      </div>

      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid #f3f4f6' }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ padding: '14px 20px', border: 'none', background: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: tab === t ? 700 : 400, color: tab === t ? '#166534' : '#6b7280', cursor: 'pointer', borderBottom: tab === t ? '2.5px solid #166534' : '2.5px solid transparent', marginBottom: -1, whiteSpace: 'nowrap' }}>
              {t}
            </button>
          ))}
        </div>

        {/* Orders list */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {filtered.map((order, i) => (
            <div key={order.id} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '18px 22px', borderBottom: i < filtered.length - 1 ? '1px solid #f9fafb' : 'none' }}>
              <div style={{ width: 64, height: 64, borderRadius: 12, overflow: 'hidden', background: '#f3f4f6', flexShrink: 0, border: '1px solid #e7f0eb' }}>
                <img src={order.image} alt={order.product} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827' }}>{order.product}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#9ca3af', marginTop: 2 }}>{order.id} • {order.date}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#374151', marginTop: 3 }}>{order.qty} — {order.price}</div>
              </div>
              <StatusPill status={order.status} />
              <button onClick={() => navigate('/consumer/orders/' + order.id)}
                style={{ padding: '8px 18px', borderRadius: 9, border: '1.5px solid #e5e7eb', background: 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#374151', cursor: 'pointer' }}>
                View Details
              </button>
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, color: '#9ca3af' }}>No orders found</div>
          )}
        </div>
      </div>
    </div>
  )
}
