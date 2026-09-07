import { useNavigate } from 'react-router'
import { ChevronRight, Check, MessageCircle } from 'lucide-react'
import { ORDER_DETAIL } from '../data/consumerData'

export default function ConsumerOrderDetail() {
  const navigate = useNavigate()
  const o = ORDER_DETAIL
  const a = o.address

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22, padding: '24px 32px' }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>
        <button onClick={() => navigate('/consumer/orders')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#166534', fontWeight: 600, padding: 0 }}>My Orders</button>
        <ChevronRight size={14} />
        <span style={{ color: '#374151', fontWeight: 600 }}>{o.id}</span>
      </div>

      {/* Title row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0, flex: 1 }}>Order Details</h1>
        <button style={{ padding: '8px 18px', borderRadius: 9, border: '1.5px solid #e5e7eb', background: 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#374151', cursor: 'pointer' }}>Reorder</button>
      </div>

      {/* Order ID + status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontFamily: 'var(--agri-font)', fontSize: 18, fontWeight: 700, color: '#111827' }}>Order #{o.id}</span>
        <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#16a34a', background: '#dcfce7', padding: '4px 12px', borderRadius: 20 }}>{o.status}</span>
      </div>
      <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#9ca3af', marginTop: -14 }}>Placed on {o.date}</div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

          {/* Items */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #f3f4f6', fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>Items</div>
            <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 56, height: 56, borderRadius: 10, overflow: 'hidden', background: '#f3f4f6', flexShrink: 0, border: '1px solid #e7f0eb' }}>
                <img src={o.item.image} alt={o.item.product} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827' }}>{o.item.product}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#9ca3af' }}>{o.item.qty} • {o.item.perUnit}</div>
              </div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>{o.item.price}</div>
            </div>
          </div>

          {/* Price Details */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #f3f4f6', fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>Price Details</div>
            <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[['Subtotal', o.subtotal], ['Delivery Charge', o.delivery]].map(([label, val]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280' }}>{label}</span>
                  <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151' }}>{val}</span>
                </div>
              ))}
              <div style={{ height: 1, background: '#f3f4f6' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>Total</span>
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 800, color: '#166534' }}>{o.total}</span>
              </div>
            </div>
          </div>

          {/* Delivery Address */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '20px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 12 }}>Delivery Address</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#374151' }}>{a.name}</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', marginTop: 4, lineHeight: 1.6 }}>{a.line1}<br />{a.line2}<br />{a.state}</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#9ca3af', marginTop: 6 }}>{a.phone}</div>
          </div>

          {/* Need Help */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '20px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 12 }}>Need Help?</div>
            <button style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, width: '100%', padding: '11px', background: 'white', border: '1.5px solid #e5e7eb', borderRadius: 9, fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#374151', cursor: 'pointer' }}>
              <MessageCircle size={16} color="#166534" /> Contact Support
            </button>
          </div>
        </div>

        {/* Order Tracking */}
        <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px', alignSelf: 'start' }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 22 }}>Order Tracking</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {o.tracking.map((t, i) => (
              <div key={t.step} style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: 26, height: 26, borderRadius: '50%', background: t.done ? '#166534' : '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    {t.done ? <Check size={13} color="white" strokeWidth={3} /> : null}
                  </div>
                  {i < o.tracking.length - 1 && <div style={{ width: 2, height: 32, background: t.done ? '#bbf7d0' : '#e5e7eb', marginTop: 2 }} />}
                </div>
                <div style={{ paddingBottom: i < o.tracking.length - 1 ? 16 : 0, paddingTop: 2 }}>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: t.done ? '#111827' : '#9ca3af' }}>{t.step}</div>
                  {t.done && <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af', marginTop: 2 }}>{t.time}</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
