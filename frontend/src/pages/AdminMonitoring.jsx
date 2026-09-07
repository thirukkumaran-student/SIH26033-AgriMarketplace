import { useState } from 'react'
import { MONITORING_STATS, USERS_LIST, PRODUCE_LISTINGS } from '../data/adminData'

function StatusPill({ status }) {
  const map = { Verified: { bg: '#dcfce7', color: '#16a34a' }, Active: { bg: '#dbeafe', color: '#2563eb' }, Pending: { bg: '#fef3c7', color: '#d97706' } }
  const s = map[status] || { bg: '#f3f4f6', color: '#6b7280' }
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 10px', borderRadius: 20 }}>{status}</span>
}

export default function AdminMonitoring() {
  const [tab, setTab] = useState('Users')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Platform Monitoring</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Overview of all platform users and listings</p>
      </div>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14 }}>
        {MONITORING_STATS.map(s => (
          <div key={s.label} style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ width: 42, height: 42, borderRadius: 12, background: s.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 18, fontWeight: 800, color: s.color }}>{s.value.slice(0,1)}</span>
            </div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 26, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid #f3f4f6' }}>
          {['Users', 'Produce Listings'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ padding: '14px 24px', border: 'none', background: 'none', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: tab === t ? 700 : 400, color: tab === t ? '#166534' : '#6b7280', cursor: 'pointer', borderBottom: tab === t ? '2.5px solid #166534' : '2.5px solid transparent', marginBottom: -1 }}>
              {t}
            </button>
          ))}
        </div>

        {tab === 'Users' ? (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb' }}>
                {['Name', 'Role', 'Contact', 'Status', 'Joined'].map(h => (
                  <th key={h} style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '11px 16px', textAlign: 'left', borderBottom: '1px solid #f3f4f6' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {USERS_LIST.map((u, i) => (
                <tr key={u.name} style={{ borderBottom: i < USERS_LIST.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                  <td style={{ padding: '13px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 700, color: '#166534' }}>{u.name.slice(0,2).toUpperCase()}</div>
                      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{u.name}</span>
                    </div>
                  </td>
                  <td style={{ padding: '13px 16px' }}>
                    <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#374151', background: '#f3f4f6', padding: '3px 9px', borderRadius: 6 }}>{u.role}</span>
                  </td>
                  <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{u.contact}</td>
                  <td style={{ padding: '13px 16px' }}><StatusPill status={u.status} /></td>
                  <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{u.joined}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb' }}>
                {['Product', 'Farmer', 'Quantity', 'Price', 'Status'].map(h => (
                  <th key={h} style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '11px 16px', textAlign: 'left', borderBottom: '1px solid #f3f4f6' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PRODUCE_LISTINGS.map((p, i) => (
                <tr key={p.product} style={{ borderBottom: i < PRODUCE_LISTINGS.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                  <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{p.product}</td>
                  <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{p.farmer}</td>
                  <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{p.qty}</td>
                  <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#166534' }}>{p.price}</td>
                  <td style={{ padding: '13px 16px' }}><StatusPill status={p.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
