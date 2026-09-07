import { useState } from 'react'
import { useNavigate } from 'react-router'
import { ALL_DISPUTES } from '../data/adminData'

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

const TABS = ['All', 'Open', 'Under Review', 'Resolved']

export default function AdminDisputes() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('All')

  const filtered = tab === 'All' ? ALL_DISPUTES : ALL_DISPUTES.filter(d => d.status === tab)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Disputes</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Review and resolve platform disputes</p>
      </div>

      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid #f3f4f6' }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ padding: '14px 22px', border: 'none', background: 'none', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: tab === t ? 700 : 400, color: tab === t ? '#166534' : '#6b7280', cursor: 'pointer', borderBottom: tab === t ? '2.5px solid #166534' : '2.5px solid transparent', marginBottom: -1, transition: 'all 0.15s' }}>
              {t}
            </button>
          ))}
        </div>

        {/* Table */}
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb' }}>
              {['Dispute ID', 'Order ID', 'Raised By', 'Issue', 'Priority', 'Status', 'Action'].map(h => (
                <th key={h} style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '11px 16px', textAlign: 'left', borderBottom: '1px solid #f3f4f6' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((d, i) => (
              <tr key={d.id} style={{ borderBottom: i < filtered.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#374151' }}>{d.id}</td>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{d.orderId}</td>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{d.raisedBy}</td>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{d.issue}</td>
                <td style={{ padding: '13px 16px' }}><PriorityPill priority={d.priority} /></td>
                <td style={{ padding: '13px 16px' }}><StatusPill status={d.status} /></td>
                <td style={{ padding: '13px 16px' }}>
                  <button onClick={() => navigate('/admin/disputes/' + d.id)}
                    style={{ padding: '7px 16px', borderRadius: 8, border: 'none', background: '#166534', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'white', cursor: 'pointer' }}>
                    {d.status === 'Resolved' ? 'View' : 'Resolve'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, color: '#9ca3af' }}>No disputes found</div>
        )}
      </div>
    </div>
  )
}
