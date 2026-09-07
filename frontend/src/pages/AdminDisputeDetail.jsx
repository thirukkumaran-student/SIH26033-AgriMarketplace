import { useNavigate } from 'react-router'
import { ChevronRight, Phone, Mail, Package } from 'lucide-react'
import { DISPUTE_DETAIL } from '../data/adminData'

function StatusPill({ status }) {
  const map = { Open: { bg: '#fee2e2', color: '#dc2626' }, 'Under Review': { bg: '#dbeafe', color: '#2563eb' }, Resolved: { bg: '#dcfce7', color: '#16a34a' } }
  const s = map[status] || { bg: '#f3f4f6', color: '#6b7280' }
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 10px', borderRadius: 20 }}>{status}</span>
}

function PriorityPill({ priority }) {
  const map = { High: { bg: '#fee2e2', color: '#dc2626' }, Medium: { bg: '#fef3c7', color: '#d97706' }, Low: { bg: '#f3f4f6', color: '#6b7280' } }
  const s = map[priority] || map.Low
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 10px', borderRadius: 20 }}>{priority}</span>
}

export default function AdminDisputeDetail() {
  const navigate = useNavigate()
  const d = DISPUTE_DETAIL
  const o = d.order

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>
        <button onClick={() => navigate('/admin/disputes')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#166534', fontWeight: 600, padding: 0 }}>Disputes</button>
        <ChevronRight size={14} />
        <span style={{ color: '#374151', fontWeight: 600 }}>{d.id}</span>
      </div>

      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 22, fontWeight: 800, color: '#111827', margin: 0, flex: 1 }}>Dispute #{d.id}</h1>
        <PriorityPill priority={d.priority} />
        <StatusPill status={d.status} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

          {/* Parties */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <PartyCard title="Consumer (Complainant)" person={d.consumer} bgColor="#dbeafe" textColor="#2563eb" />
            <PartyCard title="Farmer (Respondent)" person={d.farmer} bgColor="#dcfce7" textColor="#166534" />
          </div>

          {/* Issue Details */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 14 }}>Issue Details</div>
            <div style={{ marginBottom: 8 }}>
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Issue Type</span>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginTop: 4 }}>{d.issueType}</div>
            </div>
            <div style={{ marginBottom: 8 }}>
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Raised On</span>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151', marginTop: 4 }}>{d.raisedOn}</div>
            </div>
            <div>
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Description</span>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151', marginTop: 4, lineHeight: 1.6 }}>{d.description}</div>
            </div>
          </div>

          {/* Order Summary */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 16 }}>Order Summary</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '16px', background: '#f9fafb', borderRadius: 10, marginBottom: 16 }}>
              <div style={{ width: 52, height: 52, borderRadius: 12, background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#166534' }}>
                <Package size={22} />
              </div>
              <div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>{o.product}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{o.qty}</div>
              </div>
              <div style={{ marginLeft: 'auto', fontFamily: 'var(--agri-font)', fontSize: 18, fontWeight: 800, color: '#111827' }}>{o.total}</div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {[['Order ID', d.orderId], ['Order Date', o.orderDate], ['Delivery Date', o.deliveryDate], ['Payment', o.payment], ['Delivery Address', o.deliveryAddr], ['Order Status', o.orderStatus]].map(([label, val]) => (
                <div key={label}>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>{label}</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151' }}>{val}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resolution Actions */}
        <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px', alignSelf: 'start' }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 16 }}>Resolution Actions</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { label: 'Contact Parties', bg: '#166534', color: 'white' },
              { label: 'Request More Info', bg: 'white', color: '#374151', border: '#e5e7eb' },
              { label: 'Reject Claim', bg: 'white', color: '#dc2626', border: '#fecaca' },
              { label: 'Resolve Dispute', bg: '#166534', color: 'white' },
            ].map(({ label, bg, color, border }) => (
              <button key={label}
                style={{ width: '100%', padding: '12px', borderRadius: 9, border: `1.5px solid ${border || bg}`, background: bg, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color, cursor: 'pointer' }}>
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function PartyCard({ title, person, bgColor, textColor }) {
  return (
    <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '20px 22px' }}>
      <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 14 }}>{title}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: '50%', background: bgColor, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: textColor }}>
          {person.name.slice(0,2).toUpperCase()}
        </div>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>{person.name}</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>
          <Phone size={14} color="#9ca3af" /> {person.phone}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>
          <Mail size={14} color="#9ca3af" /> {person.email}
        </div>
      </div>
    </div>
  )
}
