import { useNavigate } from 'react-router'
import { Users, UserCheck, ShoppingBag, AlertTriangle, ChevronRight, Clock } from 'lucide-react'
import { ADMIN_STATS, VERIFICATION_QUEUE, OPEN_DISPUTES, RECENT_ACTIVITY } from '../data/adminData'

function StatCard({ icon, label, value, change, bg, color }) {
  return (
    <div style={{ background: 'white', borderRadius: 14, padding: '20px 22px', border: '1px solid #e7f0eb', display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>
          {icon}
        </div>
        <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#16a34a', background: '#dcfce7', padding: '3px 9px', borderRadius: 20 }}>{change}</span>
      </div>
      <div>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 30, fontWeight: 800, color: '#111827', lineHeight: 1.1 }}>{value}</div>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', marginTop: 4 }}>{label}</div>
      </div>
    </div>
  )
}

function StatusPill({ status }) {
  const map = {
    Pending:       { bg: '#fef3c7', color: '#d97706' },
    Approved:      { bg: '#dcfce7', color: '#16a34a' },
    Rejected:      { bg: '#fee2e2', color: '#dc2626' },
    Open:          { bg: '#fee2e2', color: '#dc2626' },
    'Under Review':{ bg: '#dbeafe', color: '#2563eb' },
    Resolved:      { bg: '#dcfce7', color: '#16a34a' },
  }
  const s = map[status] || { bg: '#f3f4f6', color: '#6b7280' }
  return (
    <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 10px', borderRadius: 20 }}>
      {status}
    </span>
  )
}

function PriorityPill({ priority }) {
  const map = { High: { bg: '#fee2e2', color: '#dc2626' }, Medium: { bg: '#fef3c7', color: '#d97706' }, Low: { bg: '#f3f4f6', color: '#6b7280' } }
  const s = map[priority] || map.Low
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 10px', borderRadius: 20 }}>{priority}</span>
}

export default function AdminDashboard() {
  const navigate = useNavigate()
  const s = ADMIN_STATS

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0, letterSpacing: '-0.01em' }}>Admin Dashboard</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Platform overview and moderation</p>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        <StatCard icon={<Users size={20} />}         label="Total Farmers"        value={s.totalFarmers.value}        change={s.totalFarmers.change}        bg="#dcfce7" color="#166534" />
        <StatCard icon={<UserCheck size={20} />}      label="Pending Verification" value={s.pendingVerification.value} change={s.pendingVerification.change} bg="#fef3c7" color="#d97706" />
        <StatCard icon={<ShoppingBag size={20} />}    label="Active Listings"      value={s.activeListings.value}      change={s.activeListings.change}      bg="#dbeafe" color="#2563eb" />
        <StatCard icon={<AlertTriangle size={20} />}  label="Open Disputes"        value={s.openDisputes.value}        change={s.openDisputes.change}        bg="#fee2e2" color="#dc2626" />
      </div>

      {/* Middle row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>

        {/* Verification Queue */}
        <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid #f3f4f6' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>Verification Queue</div>
            <button onClick={() => navigate('/admin/verification')} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>View all <ChevronRight size={14} /></button>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb' }}>
                {['Farmer', 'ID', 'Submitted', 'Docs', 'Status'].map(h => (
                  <th key={h} style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '10px 16px', textAlign: 'left', borderBottom: '1px solid #f3f4f6' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {VERIFICATION_QUEUE.map((f, i) => (
                <tr key={f.id} style={{ borderBottom: i < VERIFICATION_QUEUE.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 34, height: 34, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 700, color: '#166534' }}>{f.avatar}</div>
                      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{f.name}</span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{f.id}</td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{f.submitted}</td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{f.docs} docs</td>
                  <td style={{ padding: '12px 16px' }}><StatusPill status={f.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Open Disputes */}
        <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid #f3f4f6' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>Open Disputes</div>
            <button onClick={() => navigate('/admin/disputes')} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>View all <ChevronRight size={14} /></button>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb' }}>
                {['ID', 'Issue', 'Priority', 'Status'].map(h => (
                  <th key={h} style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '10px 16px', textAlign: 'left', borderBottom: '1px solid #f3f4f6' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {OPEN_DISPUTES.map((d, i) => (
                <tr key={d.id} style={{ borderBottom: i < OPEN_DISPUTES.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{d.id}</td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{d.issue}</td>
                  <td style={{ padding: '12px 16px' }}><PriorityPill priority={d.priority} /></td>
                  <td style={{ padding: '12px 16px' }}><StatusPill status={d.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Activity */}
      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827' }}>Recent Activity</div>
        </div>
        <div style={{ padding: '8px 20px 16px' }}>
          {RECENT_ACTIVITY.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 0', borderBottom: i < RECENT_ACTIVITY.length - 1 ? '1px solid #f9fafb' : 'none' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: a.color, flexShrink: 0 }} />
              <div style={{ flex: 1, fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151' }}>{a.text}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>
                <Clock size={12} /> {a.time}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
