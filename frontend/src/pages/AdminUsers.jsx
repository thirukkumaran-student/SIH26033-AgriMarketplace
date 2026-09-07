import { useState } from 'react'
import { USERS_LIST } from '../data/adminData'
import { Search, UserCheck, ShieldAlert, Filter, UserPlus } from 'lucide-react'

export default function AdminUsers() {
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('All')

  const roles = ['All', 'Farmer', 'Consumer', 'Bulk Buyer', 'Financier', 'Logistics']

  const filtered = USERS_LIST.filter(u => {
    const matchesSearch = u.name.toLowerCase().includes(search.toLowerCase()) || u.contact.includes(search)
    const matchesRole = roleFilter === 'All' || u.role === roleFilter
    return matchesSearch && matchesRole
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, fontFamily: 'var(--agri-font)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Platform Users</h1>
          <p style={{ fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Manage all registered farmers, consumers, buyers, and partners</p>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 260, maxWidth: 360 }}>
          <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
          <input
            placeholder="Search by name or contact..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ width: '100%', padding: '9px 12px 9px 36px', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 14, outline: 'none', background: 'white' }}
          />
        </div>

        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {roles.map(r => (
            <button
              key={r}
              onClick={() => setRoleFilter(r)}
              style={{
                padding: '7px 14px',
                borderRadius: 8,
                border: '1px solid #e5e7eb',
                background: roleFilter === r ? '#166534' : 'white',
                color: roleFilter === r ? 'white' : '#4b5563',
                fontSize: 13,
                fontWeight: roleFilter === r ? 600 : 500,
                cursor: 'pointer',
              }}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Users table */}
      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb', borderBottom: '1px solid #f3f4f6' }}>
              {['User', 'Role', 'Contact', 'Status', 'Joined Date', 'Actions'].map(h => (
                <th key={h} style={{ fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '12px 18px', textAlign: 'left' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((u, i) => (
              <tr key={u.name} style={{ borderBottom: i < filtered.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                <td style={{ padding: '14px 18px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 38, height: 38, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 14, color: '#166534' }}>
                      {u.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600, color: '#111827' }}>{u.name}</div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#374151', fontWeight: 500 }}>{u.role}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#6b7280' }}>{u.contact}</td>
                <td style={{ padding: '14px 18px' }}>
                  <span style={{
                    fontSize: 12, fontWeight: 600, padding: '4px 10px', borderRadius: 20,
                    background: u.status === 'Verified' ? '#dcfce7' : '#dbeafe',
                    color: u.status === 'Verified' ? '#16a34a' : '#2563eb',
                  }}>
                    {u.status}
                  </span>
                </td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#6b7280' }}>{u.joined}</td>
                <td style={{ padding: '14px 18px' }}>
                  <button style={{ padding: '6px 14px', background: 'white', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 13, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>
                    View Profile
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
