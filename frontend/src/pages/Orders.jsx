import { useState } from 'react'
import { useNavigate } from 'react-router'
import { ORDERS_LIST, ORDER_STATUS_VARIANT, ORDER_STATUS_OPTIONS, formatPrice } from '../data'
import { Th, Td, StatusPill } from './Dashboard'
import { SearchInput, FilterSelect, Pagination, Empty } from './MyProduce'

const GRID   = '1fr 1fr 1fr 0.8fr 0.9fr 1fr 0.9fr 80px'
const COLS   = ['Order ID','Product','Buyer','Quantity','Total','Status','Date','Action']
const PER_PAGE = 5
const TIME_OPTIONS = ['All Time', 'Last 7 Days', 'Last 30 Days']

export default function Orders() {
  const navigate             = useNavigate()
  const [search, setSearch]  = useState('')
  const [status, setStatus]  = useState('All Status')
  const [time,   setTime]    = useState('All Time')
  const [page,   setPage]    = useState(1)

  const filtered = ORDERS_LIST.filter(o => {
    const q = search.toLowerCase()
    return (
      (o.product.toLowerCase().includes(q) || o.id.toLowerCase().includes(q) || o.buyer.toLowerCase().includes(q)) &&
      (status === 'All Status' || o.status === status)
    )
  })

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE))
  const pageItems  = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE)

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Orders</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>View and manage orders for your produce</p>
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        <SearchInput value={search} onChange={v => { setSearch(v); setPage(1) }} placeholder="Search orders..." />
        <FilterSelect value={status} onChange={v => { setStatus(v); setPage(1) }} options={ORDER_STATUS_OPTIONS} />
        <FilterSelect value={time}   onChange={v => { setTime(v);   setPage(1) }} options={TIME_OPTIONS} />
      </div>

      <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: GRID, padding: '12px 20px', background: '#F8FAFB', borderBottom: '1px solid var(--agri-border)' }}>
          {COLS.map(c => <Th key={c}>{c}</Th>)}
        </div>

        {pageItems.length === 0
          ? <Empty text="No orders found" />
          : pageItems.map((row, i) => (
            <div key={row.id} style={{ display: 'grid', gridTemplateColumns: GRID, padding: '13px 20px', alignItems: 'center', borderBottom: i < pageItems.length - 1 ? '1px solid var(--agri-border-light)' : 'none' }}>
              <Td green bold>#{row.id}</Td>
              <Td>{row.product}</Td>
              <Td>{row.buyer}</Td>
              <Td>{row.qty} {row.unit}</Td>
              <Td bold>{formatPrice(row.total)}</Td>
              <StatusPill status={row.status} variant={ORDER_STATUS_VARIANT[row.status]} />
              <Td muted>{row.date}</Td>
              <button onClick={() => navigate(`/orders/${row.id}`)}
                style={{ padding: '6px 14px', background: 'white', border: '1px solid var(--agri-border)', borderRadius: 8, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: 'var(--agri-primary)', cursor: 'pointer' }}>
                View
              </button>
            </div>
          ))
        }

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 20px', borderTop: '1px solid var(--agri-border)' }}>
          <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)' }}>
            Showing {Math.min((page-1)*PER_PAGE+1, filtered.length)}–{Math.min(page*PER_PAGE, filtered.length)} of {filtered.length} orders
          </span>
          <Pagination page={page} total={totalPages} onChange={setPage} />
        </div>
      </section>
    </div>
  )
}
