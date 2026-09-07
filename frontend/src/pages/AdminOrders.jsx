import { useState } from 'react'
import { Search, Package, CheckCircle2 } from 'lucide-react'

const ORDERS_DATA = [
  { id: 'ORD-1042', product: 'Organic Tomatoes', farmer: 'Ravi Kumar', buyer: 'Anita Sharma (Consumer)', amount: '₹1,250', date: '02 Sep 2025', status: 'Delivered' },
  { id: 'ORD-1039', product: 'Ponni Raw Rice', farmer: 'Suresh', buyer: 'Gibtel Foods (Bulk)', amount: '₹42,000', date: '01 Sep 2025', status: 'Shipped' },
  { id: 'ORD-1035', product: 'Alphonso Mangoes', farmer: 'Priya Kumar', buyer: 'Kavitha R (Consumer)', amount: '₹2,400', date: '31 Aug 2025', status: 'Processing' },
  { id: 'ORD-1028', product: 'Groundnut High Grade', farmer: 'Arun Kumar', buyer: 'AgriExport Co (Bulk)', amount: '₹18,500', date: '29 Aug 2025', status: 'Delivered' },
  { id: 'ORD-1021', product: 'Fresh Banana (Robusta)', farmer: 'Selvam', buyer: 'GreenMart (Bulk)', amount: '₹12,000', date: '27 Aug 2025', status: 'Delivered' },
]

export default function AdminOrders() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const filtered = ORDERS_DATA.filter(o => {
    const matchesSearch = o.id.toLowerCase().includes(search.toLowerCase()) ||
                          o.farmer.toLowerCase().includes(search.toLowerCase()) ||
                          o.buyer.toLowerCase().includes(search.toLowerCase())
    const matchesFilter = filter === 'All' || o.status === filter
    return matchesSearch && matchesFilter
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, fontFamily: 'var(--agri-font)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Platform Orders Overview</h1>
          <p style={{ fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Real-time transactions between farmers, consumers, and bulk buyers</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <div style={{ position: 'relative', maxWidth: 360, flex: 1 }}>
          <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
          <input
            placeholder="Search by order, farmer, or buyer..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ width: '100%', padding: '9px 12px 9px 36px', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 14, outline: 'none', background: 'white' }}
          />
        </div>

        {['All', 'Delivered', 'Shipped', 'Processing'].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{
              padding: '7px 14px',
              borderRadius: 8,
              border: '1px solid #e5e7eb',
              background: filter === s ? '#166534' : 'white',
              color: filter === s ? 'white' : '#4b5563',
              fontSize: 13,
              fontWeight: filter === s ? 600 : 500,
              cursor: 'pointer',
            }}
          >
            {s}
          </button>
        ))}
      </div>

      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb', borderBottom: '1px solid #f3f4f6' }}>
              {['Order ID', 'Produce', 'Farmer', 'Buyer', 'Amount', 'Date', 'Status'].map(h => (
                <th key={h} style={{ fontSize: 13, fontWeight: 600, color: '#6b7280', padding: '12px 18px', textAlign: 'left' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((o, i) => (
              <tr key={o.id} style={{ borderBottom: i < filtered.length - 1 ? '1px solid #f9fafb' : 'none' }}>
                <td style={{ padding: '14px 18px', fontSize: 14, fontWeight: 700, color: '#166534' }}>{o.id}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, fontWeight: 600, color: '#111827' }}>{o.product}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#374151' }}>{o.farmer}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#6b7280' }}>{o.buyer}</td>
                <td style={{ padding: '14px 18px', fontSize: 15, fontWeight: 700, color: '#111827' }}>{o.amount}</td>
                <td style={{ padding: '14px 18px', fontSize: 14, color: '#6b7280' }}>{o.date}</td>
                <td style={{ padding: '14px 18px' }}>
                  <span style={{
                    fontSize: 12, fontWeight: 600, padding: '4px 10px', borderRadius: 20,
                    background: o.status === 'Delivered' ? '#dcfce7' : o.status === 'Shipped' ? '#dbeafe' : '#fef3c7',
                    color: o.status === 'Delivered' ? '#16a34a' : o.status === 'Shipped' ? '#2563eb' : '#d97706',
                  }}>
                    {o.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
