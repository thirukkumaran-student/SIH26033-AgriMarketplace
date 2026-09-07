import { useNavigate } from 'react-router'
import { CheckCircle, Sprout, ShoppingCart, BarChart3, ShieldCheck } from 'lucide-react'
import {
  PRODUCE_LIST, ORDERS_LIST, PRODUCE_IMAGES, DEFAULT_IMG,
  ORDER_STATUS_VARIANT, PRODUCE_STATUS_VARIANT, formatPrice,
} from '../data'

// ── Shared table primitives exported for reuse across all pages ──────────
export function Th({ children }) {
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 600, color: 'var(--agri-text)' }}>{children}</span>
}
export function Td({ children, bold, green, muted }) {
  return <span style={{ fontFamily: 'var(--agri-font)', fontSize: 16, color: green ? 'var(--agri-primary)' : muted ? 'var(--agri-text-muted)' : 'var(--agri-text)', fontWeight: bold ? 600 : 400 }}>{children}</span>
}
export { TableHeadRow as TableHead }
export function TableHeadRow({ cols, grid, style }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: grid, padding: '12px 20px', background: '#F8FAFB', borderBottom: '1px solid var(--agri-border)', ...style }}>
      {cols.map(c => <Th key={c}>{c}</Th>)}
    </div>
  )
}
export function Card({ title, action, children }) {
  return (
    <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid var(--agri-border)' }}>
        <h2 style={{ fontFamily: 'var(--agri-font)', fontSize: 20, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>{title}</h2>
        {action}
      </div>
      {children}
    </section>
  )
}
export function ViewAllBtn({ onClick }) {
  return (
    <button onClick={onClick} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-primary)', fontWeight: 500 }}>
      View all →
    </button>
  )
}
export function ProduceThumb({ name }) {
  return (
    <img src={PRODUCE_IMAGES[name] || DEFAULT_IMG} alt={name}
      style={{ width: 64, height: 64, borderRadius: 10, objectFit: 'cover', flexShrink: 0 }} />
  )
}
export function GreenBtn({ onClick, children, small }) {
  return (
    <button onClick={onClick} style={{ display: 'flex', alignItems: 'center', gap: 5, background: 'var(--agri-primary)', color: 'white', border: 'none', borderRadius: 8, padding: small ? '7px 14px' : '9px 16px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>
      {children}
    </button>
  )
}
export function OutlineBtn({ onClick, children, danger }) {
  return (
    <button onClick={onClick} style={{ display: 'flex', alignItems: 'center', gap: 5, background: 'white', color: danger ? 'var(--agri-error)' : 'var(--agri-text)', border: `1px solid ${danger ? 'var(--agri-error)' : 'var(--agri-border)'}`, borderRadius: 8, padding: '8px 16px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>
      {children}
    </button>
  )
}

const RECENT_PRODUCE = PRODUCE_LIST.slice(0, 3)
const RECENT_ORDERS  = ORDERS_LIST.slice(0, 3)

export default function Dashboard() {
  const navigate = useNavigate()
  const totalRevenue = ORDERS_LIST.filter(o => o.status === 'Delivered').reduce((s, o) => s + o.total, 0)

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Greeting */}
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 26, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>
          Good morning, Ravi 👋
        </h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 16, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>
          {"Here's your farm overview"}
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16 }}>
        <StatCard
          icon={<StatIcon bg="#DCFCE7" color="#16A34A"><Sprout size={22} strokeWidth={2} /></StatIcon>}
          label="Total Produce" value={String(PRODUCE_LIST.length)} sub="Active listings"
          onClick={() => navigate('/produce')} />
        <StatCard
          icon={<StatIcon bg="#D1FAE5" color="#047857"><ShoppingCart size={22} strokeWidth={2} /></StatIcon>}
          label="Orders Received" value={String(ORDERS_LIST.length)} sub="Pending & in progress"
          onClick={() => navigate('/orders')} />
        <StatCard
          icon={<StatIcon bg="#FEF9C3" color="#854D0E"><BarChart3 size={22} strokeWidth={2} /></StatIcon>}
          label="Revenue" value={formatPrice(totalRevenue)} sub="Total earnings" />
        <StatCard
          icon={<StatIcon bg="#DCFCE7" color="#166534"><ShieldCheck size={22} strokeWidth={2} /></StatIcon>}
          label="Verification Status" value="Verified" sub="You can list produce"
          verified onClick={() => navigate('/verification')} />
      </div>

      {/* Your Produce */}
      <Card title="Your Produce" action={<ViewAllBtn onClick={() => navigate('/produce')} />}>
        <TableHeadRow cols={['Product', 'Quantity', 'Price/Unit', 'Status']} grid="2fr 1fr 1fr 1fr" />
        {RECENT_PRODUCE.map((row, i) => (
          <div key={row.id} onClick={() => navigate('/produce')}
            style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', padding: '10px 20px', alignItems: 'center', borderBottom: i < RECENT_PRODUCE.length - 1 ? '1px solid var(--agri-border-light)' : 'none', cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <ProduceThumb name={row.name} />
              <Td bold>{row.name}</Td>
            </div>
            <Td>{row.qty} {row.unit}</Td>
            <Td>₹{row.price}/{row.unit}</Td>
            <StatusPill status={row.status} variant={PRODUCE_STATUS_VARIANT[row.status]} />
          </div>
        ))}
      </Card>

      {/* Recent Orders */}
      <Card title="Recent Orders" action={<ViewAllBtn onClick={() => navigate('/orders')} />}>
        <TableHeadRow cols={['Order ID', 'Product', 'Quantity', 'Status']} grid="1.2fr 1.5fr 1fr 1fr" />
        {RECENT_ORDERS.map((row, i) => (
          <div key={row.id} onClick={() => navigate(`/orders/${row.id}`)}
            style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.5fr 1fr 1fr', padding: '13px 20px', alignItems: 'center', borderBottom: i < RECENT_ORDERS.length - 1 ? '1px solid var(--agri-border-light)' : 'none', cursor: 'pointer' }}>
            <Td green bold>#{row.id}</Td>
            <Td>{row.product}</Td>
            <Td>{row.qty} {row.unit}</Td>
            <StatusPill status={row.status} variant={ORDER_STATUS_VARIANT[row.status]} />
          </div>
        ))}
      </Card>
    </div>
  )
}

function StatCard({ icon, label, value, sub, verified, onClick }) {
  return (
    <div onClick={onClick} style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, padding: '20px', display: 'flex', gap: 16, alignItems: 'flex-start', cursor: onClick ? 'pointer' : 'default' }}>
      {icon}
      <div style={{ minWidth: 0 }}>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, color: 'var(--agri-text-secondary)', marginBottom: 4 }}>{label}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
          {verified && <CheckCircle size={16} color="var(--agri-success)" />}
          <span style={{ fontFamily: 'var(--agri-font)', fontSize: verified ? 20 : 28, fontWeight: 700, color: verified ? 'var(--agri-success)' : 'var(--agri-text)', lineHeight: 1.1 }}>{value}</span>
        </div>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)' }}>{sub}</div>
      </div>
    </div>
  )
}
function StatIcon({ bg, color, children }) {
  return (
    <div style={{ width: 52, height: 52, borderRadius: 10, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color, flexShrink: 0 }}>
      {children}
    </div>
  )
}

/* StatusPill replaces the kit Badge in table rows — pastel pill with colored dot */
export function StatusPill({ status, variant }) {
  const colors = {
    success: { bg: '#DCFCE7', dot: '#16A34A', text: '#15803D' },
    warning: { bg: '#FEF9C3', dot: '#D97706', text: '#92400E' },
    danger:  { bg: '#FEE2E2', dot: '#DC2626', text: '#991B1B' },
    info:    { bg: '#DBEAFE', dot: '#2563EB', text: '#1D4ED8' },
    neutral: { bg: '#EDE9FE', dot: '#7C3AED', text: '#5B21B6' },
  }
  const c = colors[variant] || colors.neutral
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: c.bg, color: c.text, borderRadius: 20, padding: '4px 10px', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, width: 'fit-content' }}>
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: c.dot, flexShrink: 0 }} />
      {status}
    </div>
  )
}
