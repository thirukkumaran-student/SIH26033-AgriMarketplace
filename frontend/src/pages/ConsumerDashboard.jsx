import { useNavigate } from 'react-router'
import { ChevronRight, Heart, Star, ShoppingBag, Bookmark, Users, Wallet } from 'lucide-react'
import { CONSUMER_STATS, CATEGORIES, FRESH_PICKS } from '../data/consumerData'

const STAT_ICONS = {
  'Orders Placed': ShoppingBag,
  'Favourites': Bookmark,
  'Farmers Followed': Users,
  'Total Spent': Wallet,
}

export default function ConsumerDashboard() {
  const navigate = useNavigate()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, padding: '24px 32px' }}>

      {/* Hero Banner */}
      <div style={{ borderRadius: 16, overflow: 'hidden', background: 'linear-gradient(135deg, #14532d 0%, #166534 40%, #22c55e 100%)', padding: '32px 36px', position: 'relative', minHeight: 140, display: 'flex', alignItems: 'center' }}>
        {/* decorative circles */}
        <div style={{ position: 'absolute', right: -30, top: -40, width: 220, height: 220, borderRadius: '50%', background: 'rgba(255,255,255,0.06)' }} />
        <div style={{ position: 'absolute', right: 60, bottom: -60, width: 160, height: 160, borderRadius: '50%', background: 'rgba(255,255,255,0.04)' }} />
        <div style={{ position: 'absolute', right: 180, top: 10, width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.08)' }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 30, fontWeight: 900, color: 'white', margin: '0 0 8px', letterSpacing: '-0.02em' }}>Good to see you, Ananya!</h1>
          <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'rgba(255,255,255,0.85)', margin: 0 }}>Fresh produce. Trusted farmers. A better tomorrow.</p>
        </div>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
        {CONSUMER_STATS.map(s => {
          const IconComp = STAT_ICONS[s.label] || ShoppingBag
          return (
            <div key={s.label} style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: s.bg || '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <IconComp size={22} color={s.color || '#166534'} />
              </div>
              <div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', lineHeight: 1.1 }}>{s.value}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', marginTop: 3 }}>{s.label}</div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Featured Categories */}
      <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: '#111827' }}>Featured Categories</div>
          <button onClick={() => navigate('/consumer/marketplace')} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>View All <ChevronRight size={14} /></button>
        </div>
        <div style={{ display: 'flex', gap: 20, justifyContent: 'space-between' }}>
          {CATEGORIES.map(c => (
            <button key={c.label} onClick={() => navigate('/consumer/marketplace')}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, background: 'none', border: 'none', cursor: 'pointer' }}>
              <div style={{ width: 68, height: 68, borderRadius: '50%', overflow: 'hidden', border: `2px solid ${c.color || '#166534'}20`, boxShadow: '0 2px 6px rgba(0,0,0,0.06)' }}>
                <img src={c.image} alt={c.label} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#374151' }}>{c.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Fresh Picks */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: '#111827' }}>Fresh Picks for You</div>
          <button onClick={() => navigate('/consumer/marketplace')} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>View All <ChevronRight size={14} /></button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
          {FRESH_PICKS.slice(0, 4).map(item => (
            <ProductCard key={item.id} item={item} onNavigate={() => navigate('/consumer/marketplace/' + item.id)} />
          ))}
        </div>
      </div>
    </div>
  )
}

function ProductCard({ item, onNavigate }) {
  return (
    <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden', display: 'flex', flexDirection: 'column', transition: 'transform 0.15s ease, box-shadow 0.15s ease' }}>
      <div style={{ position: 'relative' }}>
        <div style={{ height: 160, width: '100%', overflow: 'hidden', background: '#f3f4f6' }}>
          <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </div>
        <button style={{ position: 'absolute', top: 10, right: 10, width: 32, height: 32, borderRadius: '50%', background: 'white', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <Heart size={15} color="#9ca3af" />
        </button>
      </div>
      <div style={{ padding: '14px 14px 16px', flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827' }}>{item.name}</div>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 800, color: '#166534' }}>₹{item.price}/{item.unit}</div>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#6b7280' }}>{item.farmer} • {item.location}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
          <Star size={13} fill="#d97706" color="#d97706" />
          <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#374151' }}>{item.rating}</span>
          <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>({item.reviews})</span>
        </div>
        <button onClick={onNavigate}
          style={{ marginTop: 10, width: '100%', padding: '9px', background: '#166534', border: 'none', borderRadius: 8, fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'white', cursor: 'pointer' }}>
          View Details
        </button>
      </div>
    </div>
  )
}
