import { useState } from 'react'
import { useNavigate } from 'react-router'
import { SHIPMENTS_LIST, SHIPMENT_STATUS_VARIANT, SHIPMENT_STATUS_OPTIONS } from '../data'
import { Th, Td, StatusPill } from './Dashboard'
import { SearchInput, FilterSelect, Empty } from './MyProduce'

const GRID = '1fr 1fr 1.5fr 1.2fr 1fr 80px'
const COLS = ['Shipment ID', 'Order ID', 'Transporter', 'Delivery Date', 'Status', 'Action']

export default function Shipments() {
  const navigate            = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('All Status')

  const filtered = SHIPMENTS_LIST.filter(s => {
    const q = search.toLowerCase()
    return (
      (s.id.toLowerCase().includes(q) || s.orderId.toLowerCase().includes(q) || s.transporter.toLowerCase().includes(q)) &&
      (status === 'All Status' || s.status === status)
    )
  })

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Shipments</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>Track the delivery status of your orders</p>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Search shipments..." />
        <FilterSelect value={status} onChange={setStatus} options={SHIPMENT_STATUS_OPTIONS} />
      </div>

      <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: GRID, padding: '12px 20px', background: '#F8FAFB', borderBottom: '1px solid var(--agri-border)' }}>
          {COLS.map(c => <Th key={c}>{c}</Th>)}
        </div>

        {filtered.length === 0
          ? <Empty text="No shipments found" />
          : filtered.map((row, i) => (
            <div key={row.id} style={{ display: 'grid', gridTemplateColumns: GRID, padding: '13px 20px', alignItems: 'center', borderBottom: i < filtered.length - 1 ? '1px solid var(--agri-border-light)' : 'none' }}>
              <Td green bold>#{row.id}</Td>
              <button onClick={() => navigate(`/orders/${row.orderId}`)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: 'var(--agri-primary)', textAlign: 'left', padding: 0 }}>
                #{row.orderId}
              </button>
              <Td>{row.transporter}</Td>
              <Td muted>{row.deliveryDate}</Td>
              <StatusPill status={row.status} variant={SHIPMENT_STATUS_VARIANT[row.status]} />
              <button onClick={() => navigate(`/orders/${row.orderId}`)}
                style={{ padding: '6px 14px', background: 'white', border: '1px solid var(--agri-border)', borderRadius: 8, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-primary)', cursor: 'pointer' }}>
                View
              </button>
            </div>
          ))
        }
      </section>
    </div>
  )
}
