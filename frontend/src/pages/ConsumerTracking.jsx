import { useNavigate } from 'react-router'
import { ArrowLeft, CheckCircle2, Circle, Truck, MapPin, Phone, User, Package, ShieldCheck } from 'lucide-react'

const TIMELINE = [
  { step: 'Order Placed', time: '04 Sep, 10:30 AM', desc: 'Received and confirmed by Farmer Ravi Kumar', completed: true },
  { step: 'Quality Check & Packed', time: '04 Sep, 02:15 PM', desc: 'Freshly harvested and cold-packed at Thanjavur Farm', completed: true },
  { step: 'In Transit', time: '05 Sep, 08:00 AM', desc: 'Picked up by FastTrack AgriLogistics (TN-49-AB-2041)', completed: true, current: true },
  { step: 'Out for Delivery', time: 'Expected Today, 01:00 PM', desc: 'Delivery partner will deliver to your doorstep', completed: false },
  { step: 'Delivered', time: 'Expected Today, 02:00 PM', desc: 'Direct verification with consumer code', completed: false },
]

export default function ConsumerTracking() {
  const navigate = useNavigate()

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 24, fontFamily: 'var(--agri-font)' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button onClick={() => navigate('/consumer/orders')} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', cursor: 'pointer', fontSize: 14, color: '#166534', fontWeight: 700, padding: 0 }}>
          <ArrowLeft size={16} /> Back to Orders
        </button>

        <span style={{ fontSize: 13, fontWeight: 700, color: '#166534', background: '#dcfce7', padding: '6px 14px', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 6, border: '1px solid #bbf7d0' }}>
          <Truck size={15} /> Live Shipment In Transit
        </span>
      </div>

      <div>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Live Shipment Tracking</h1>
        <p style={{ fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Order #ORD-C101 · Estimated Arrival: Today by 2:00 PM</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: 24, alignItems: 'start' }}>

        {/* Left: Milestone Timeline */}
        <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 16, padding: '28px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: '#111827', margin: '0 0 24px' }}>Delivery Progress</h2>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {TIMELINE.map((t, i) => (
              <div key={t.step} style={{ display: 'flex', gap: 18, position: 'relative' }}>
                {/* Connecting line */}
                {i < TIMELINE.length - 1 && (
                  <div style={{
                    position: 'absolute', left: 14, top: 28, bottom: -8, width: 2,
                    background: t.completed && !t.current ? '#16a34a' : '#e5e7eb',
                  }} />
                )}

                {/* Dot */}
                <div style={{
                  width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: t.current ? '#166534' : t.completed ? '#dcfce7' : '#f3f4f6',
                  color: t.current ? 'white' : t.completed ? '#16a34a' : '#9ca3af',
                  boxShadow: t.current ? '0 0 0 4px #dcfce7' : 'none',
                  zIndex: 1,
                }}>
                  {t.completed ? <CheckCircle2 size={17} /> : <Circle size={10} />}
                </div>

                {/* Details */}
                <div style={{ paddingBottom: 28 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontSize: 15, fontWeight: t.current || t.completed ? 800 : 500, color: t.current ? '#166534' : t.completed ? '#111827' : '#9ca3af' }}>
                      {t.step}
                    </span>
                    <span style={{ fontSize: 13, color: '#6b7280' }}>{t.time}</span>
                  </div>
                  <p style={{ fontSize: 14, color: '#4b5563', margin: '4px 0 0' }}>{t.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Produce in Transit & Courier */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

          {/* Produce package info */}
          <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 16, padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
            <h3 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: '0 0 14px' }}>Package Contents</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <img
                src="https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=200&h=200&fit=crop&q=80"
                alt="Tomatoes"
                style={{ width: 60, height: 60, borderRadius: 10, objectFit: 'cover', border: '1px solid #edf2ef' }}
              />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#111827' }}>Farm Fresh Tomatoes (5 kg)</div>
                <div style={{ fontSize: 13, color: '#6b7280' }}>From Ravi Kumar · Thanjavur</div>
              </div>
            </div>
          </div>

          {/* Driver card */}
          <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 16, padding: '20px', display: 'flex', flexDirection: 'column', gap: 14, boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
            <h3 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: 0 }}>Driver & Vehicle Info</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 46, height: 46, borderRadius: '50%', background: '#dbeafe', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800 }}>
                MR
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#111827' }}>Muthu Raman</div>
                <div style={{ fontSize: 13, color: '#6b7280' }}>FastTrack AgriLogistics · Tata Ace (Refrigerated)</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', background: '#f0fdf4', borderRadius: 8, fontSize: 14, color: '#166534', fontWeight: 600 }}>
              <Phone size={15} />
              <span>+91 94432 88190 (Direct Call)</span>
            </div>
          </div>

          {/* Delivery destination */}
          <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 16, padding: '20px', display: 'flex', flexDirection: 'column', gap: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
            <h3 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: 0 }}>Delivery Address</h3>
            <div style={{ display: 'flex', gap: 10, fontSize: 14, color: '#4b5563', lineHeight: 1.5 }}>
              <MapPin size={18} color="#166534" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ color: '#111827' }}>Ananya Sharma</strong><br />
                Flat 4B, Green Meadows Apartment,<br />
                Anna Nagar, Chennai, Tamil Nadu - 600040
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  )
}
