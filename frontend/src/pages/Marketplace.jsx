import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Heart, Star } from 'lucide-react'
import { FRESH_PICKS } from '../data/consumerData'

const ALL_TABS = ['All', 'Fruits', 'Vegetables', 'Grains', 'Dairy', 'Spices', 'Organic']

export default function Marketplace() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('All')
  const [wishlist, setWishlist] = useState([])

  function toggleWish(id) {
    setWishlist(w => w.includes(id) ? w.filter(x => x !== id) : [...w, id])
  }

  const filtered = tab === 'All' ? FRESH_PICKS : FRESH_PICKS.filter(p => p.category === tab)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, padding: '24px 32px' }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Marketplace</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Discover fresh produce directly from verified farmers.</p>
      </div>

      {/* Category tab strip */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {ALL_TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: '8px 18px', borderRadius: 24, border: '1.5px solid', borderColor: tab === t ? '#166534' : '#e5e7eb', background: tab === t ? '#166534' : 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: tab === t ? 600 : 400, color: tab === t ? 'white' : '#374151', cursor: 'pointer', transition: 'all 0.15s' }}>
            {t}
          </button>
        ))}
      </div>

      {/* Product grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        {filtered.map(item => (
          <div key={item.id} style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ position: 'relative' }}>
              <div style={{ height: 160, width: '100%', overflow: 'hidden', background: '#f3f4f6' }}>
                <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <button onClick={() => toggleWish(item.id)}
                style={{ position: 'absolute', top: 10, right: 10, width: 32, height: 32, borderRadius: '50%', background: 'white', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <Heart size={15} color={wishlist.includes(item.id) ? '#dc2626' : '#9ca3af'} fill={wishlist.includes(item.id) ? '#dc2626' : 'none'} />
              </button>
            </div>
            <div style={{ padding: '14px 14px 16px', flex: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827' }}>{item.name}</div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 800, color: '#166534' }}>₹{item.price}/{item.unit}</div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#6b7280' }}>{item.farmer}, {item.location}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
                <Star size={13} fill="#d97706" color="#d97706" />
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#374151' }}>{item.rating}</span>
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>({item.reviews})</span>
              </div>
              <button onClick={() => navigate('/consumer/marketplace/' + item.id)}
                style={{ marginTop: 10, width: '100%', padding: '9px', background: '#166534', border: 'none', borderRadius: 8, fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'white', cursor: 'pointer' }}>
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
