import { useState } from 'react'
import { PRODUCE_LISTINGS } from '../data/adminData'
import { Search, Check, X, Eye } from 'lucide-react'

export default function AdminListings() {
  const [listings, setListings] = useState(PRODUCE_LISTINGS)
  const [search, setSearch] = useState('')

  function approveListing(index) {
    setListings(prev =>
      prev.map((l, i) => (i === index ? { ...l, status: 'Active' } : l))
    )
  }

  function delistListing(index) {
    setListings(prev =>
      prev.map((l, i) => (i === index ? { ...l, status: 'Suspended' } : l))
    )
  }

  const filtered = listings.filter(l =>
    l.product.toLowerCase().includes(search.toLowerCase()) ||
    l.farmer.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, fontFamily: 'var(--agri-font)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Produce Listings Moderation</h1>
          <p style={{ fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Review and verify farmer produce listed on the marketplace</p>
        </div>
      </div>

      {/* Search */}
      <div style={{ position: 'relative', maxWidth: 360 }}>
        <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
        <input
          placeholder="Search by produce or farmer..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ width: '100%', padding: '9px 12px 9px 36px', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 14, outline: 'none', background: 'white' }}
        />
      </div>

      {/* Listings Table */}
      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb', borderBottom: '1px solid #f3f4f6' }}>
              {['Produce Item', 'Farmer', 'Stock Quantity', 'Price per Unit', 'Listing Status', 'Actions'].map(h => (
                <th key={h} style={{ fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '12px 18px', textAlign: 'left' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((item, i) => (
              <tr key={item.product + item.farmer} style={{ borderBottom: i < filtered.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                <td style={{ padding: '14px 18px', fontSize: 15, fontWeight: 600, color: '#111827' }}>
                  {item.product}
                </td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#374151' }}>{item.farmer}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#374151' }}>{item.qty}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, fontWeight: 600, color: '#166534' }}>{item.price}</td>
                <td style={{ padding: '14px 18px' }}>
                  <span style={{
                    fontSize: 12, fontWeight: 600, padding: '4px 10px', borderRadius: 20,
                    background: item.status === 'Active' ? '#dcfce7' : item.status === 'Pending' ? '#fef3c7' : '#fee2e2',
                    color: item.status === 'Active' ? '#16a34a' : item.status === 'Pending' ? '#d97706' : '#dc2626',
                  }}>
                    {item.status}
                  </span>
                </td>
                <td style={{ padding: '14px 18px' }}>
                  <div style={{ display: 'flex', gap: 8 }}>
                    {item.status === 'Pending' && (
                      <button onClick={() => approveListing(i)} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 10px', background: '#166534', color: 'white', border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                        <Check size={13} /> Approve
                      </button>
                    )}
                    {item.status === 'Active' && (
                      <button onClick={() => delistListing(i)} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 10px', background: 'white', color: '#dc2626', border: '1px solid #fecaca', borderRadius: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                        <X size={13} /> Suspend
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
