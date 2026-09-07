import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Search } from 'lucide-react'
import { ALL_VERIFICATIONS } from '../data/adminData'

function StatusPill({ status }) {
  const map = { Pending: { bg: '#fef3c7', color: '#d97706' }, Approved: { bg: '#dcfce7', color: '#16a34a' }, Rejected: { bg: '#fee2e2', color: '#dc2626' } }
  const s = map[status] || { bg: '#f3f4f6', color: '#6b7280' }
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: s.color, background: s.bg, padding: '4px 10px', borderRadius: 20 }}>{status}</span>
}

export default function FarmerVerification() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('All')

  const FILTERS = ['All', 'Pending', 'Approved', 'Rejected']

  const filtered = ALL_VERIFICATIONS.filter(f => {
    const matchQ = query === '' || f.name.toLowerCase().includes(query.toLowerCase()) || f.id.toLowerCase().includes(query.toLowerCase())
    const matchF = filter === 'All' || f.status === filter
    return matchQ && matchF
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Farmer Verification</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Review and verify farmer registrations</p>
      </div>

      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        {/* Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '16px 20px', borderBottom: '1px solid #f3f4f6', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 200, border: '1.5px solid #e5e7eb', borderRadius: 9, padding: '8px 12px', background: '#f9fafb' }}>
            <Search size={15} color="#9ca3af" />
            <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search by name or ID..." style={{ flex: 1, border: 'none', background: 'transparent', fontFamily: 'var(--agri-font)', fontSize: 14, outline: 'none', color: '#374151' }} />
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            {FILTERS.map(f => (
              <button key={f} onClick={() => setFilter(f)}
                style={{ padding: '7px 14px', borderRadius: 9, border: '1.5px solid', borderColor: filter === f ? '#166534' : '#e5e7eb', background: filter === f ? '#f0fdf4' : 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: filter === f ? 600 : 400, color: filter === f ? '#166534' : '#374151', cursor: 'pointer' }}>
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb' }}>
              {['Farmer', 'Contact', 'District', 'Submitted', 'Docs', 'Status', 'Action'].map(h => (
                <th key={h} style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '11px 16px', textAlign: 'left', borderBottom: '1px solid #f3f4f6' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((f, i) => (
              <tr key={f.id} style={{ borderBottom: i < filtered.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                <td style={{ padding: '13px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
                    <div style={{ width: 38, height: 38, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 700, color: '#166534', flexShrink: 0 }}>{f.avatar}</div>
                    <div>
                      <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{f.name}</div>
                      <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>{f.id}</div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{f.phone}</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>{f.email}</div>
                </td>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{f.district}</td>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{f.submitted}</td>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>{f.docs} docs</td>
                <td style={{ padding: '13px 16px' }}><StatusPill status={f.status} /></td>
                <td style={{ padding: '13px 16px' }}>
                  <button onClick={() => navigate('/admin/verification/' + f.id)}
                    style={{ padding: '7px 16px', borderRadius: 8, border: 'none', background: '#166534', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'white', cursor: 'pointer' }}>
                    {f.status === 'Pending' ? 'Review' : 'View'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div style={{ padding: '40px 20px', textAlign: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, color: '#9ca3af' }}>
            No results found
          </div>
        )}
      </div>
    </div>
  )
}
