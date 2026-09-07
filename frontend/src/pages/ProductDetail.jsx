import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { ChevronRight, Heart, Minus, Plus, Star, Check } from 'lucide-react'
import { FRESH_PICKS } from '../data/consumerData'

export default function ProductDetail() {
  const navigate = useNavigate()
  const { id } = useParams()
  const item = FRESH_PICKS.find(p => String(p.id) === String(id)) || FRESH_PICKS[0]
  
  const gallery = item.gallery && item.gallery.length > 0 ? item.gallery : [item.image]
  const [selectedImg, setSelectedImg] = useState(0)
  const [qty, setQty] = useState(1)
  const [wished, setWished] = useState(false)

  const similarItems = FRESH_PICKS.filter(p => p.id !== item.id).slice(0, 5)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, padding: '24px 32px' }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>
        <button onClick={() => navigate('/consumer/marketplace')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#166534', fontWeight: 600, padding: 0 }}>Marketplace</button>
        <ChevronRight size={14} />
        <span style={{ color: '#9ca3af' }}>{item.category}</span>
        <ChevronRight size={14} />
        <span style={{ color: '#374151', fontWeight: 600 }}>{item.name}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
        {/* Left images */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ height: 340, borderRadius: 16, overflow: 'hidden', border: '1px solid #e7f0eb', background: '#f9fafb' }}>
            <img src={gallery[selectedImg] || item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            {gallery.map((imgUrl, i) => (
              <div key={i} onClick={() => setSelectedImg(i)}
                style={{ width: 80, height: 80, borderRadius: 10, overflow: 'hidden', border: `2px solid ${selectedImg === i ? '#166534' : '#e7f0eb'}`, cursor: 'pointer', background: '#f9fafb' }}>
                <img src={imgUrl} alt={`${item.name} ${i}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
            ))}
          </div>
        </div>

        {/* Right details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 26, fontWeight: 900, color: '#111827', margin: '0 0 6px' }}>{item.name}</h1>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#166534', marginBottom: 8 }}>₹{item.price}/{item.unit}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Star size={16} fill="#d97706" color="#d97706" />
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827' }}>{item.rating}</span>
              <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#9ca3af' }}>({item.reviews} reviews)</span>
            </div>
          </div>

          {/* Badges */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {['Fresh', 'Chemical Free', 'Locally Grown'].map(b => (
              <span key={b} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#166534', background: '#dcfce7', padding: '4px 10px', borderRadius: 20, border: '1px solid #bbf7d0' }}>
                <Check size={13} strokeWidth={3} /> {b}
              </span>
            ))}
          </div>

          {/* Seller */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px', background: '#f9fafb', borderRadius: 12, border: '1px solid #e5e7eb' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 42, height: 42, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#166534' }}>
                {item.farmer ? item.farmer.slice(0, 2).toUpperCase() : 'AG'}
              </div>
              <div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 700, color: '#111827' }}>Sold by {item.farmer}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>{item.location}, Tamil Nadu</div>
              </div>
            </div>
            <button style={{ padding: '7px 14px', borderRadius: 8, border: '1.5px solid #166534', background: 'white', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>View Farm</button>
          </div>

          {/* Description */}
          <div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827', marginBottom: 6 }}>About this product</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', lineHeight: 1.6 }}>
              {item.description || `Fresh, farm-grown ${item.name.toLowerCase()} with rich taste and natural freshness. Grown without harmful chemicals. Ideal for daily cooking.`}
            </div>
          </div>

          {/* Meta row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            {[['Available Qty', '500 kg'], ['Harvest Date', '02 Sep 2025'], ['Delivery', '2–3 days']].map(([label, val]) => (
              <div key={label} style={{ background: '#f9fafb', borderRadius: 10, padding: '10px 12px' }}>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 3 }}>{label}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 700, color: '#111827' }}>{val}</div>
              </div>
            ))}
          </div>

          {/* Qty selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151', fontWeight: 600 }}>Quantity:</span>
            <div style={{ display: 'flex', alignItems: 'center', border: '1.5px solid #e5e7eb', borderRadius: 9, overflow: 'hidden' }}>
              <button onClick={() => setQty(q => Math.max(1, q - 1))} style={{ width: 36, height: 36, background: '#f9fafb', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#374151' }}><Minus size={14} /></button>
              <span style={{ width: 40, textAlign: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#111827' }}>{qty}</span>
              <button onClick={() => setQty(q => q + 1)} style={{ width: 36, height: 36, background: '#f9fafb', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#374151' }}><Plus size={14} /></button>
            </div>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{item.unit}</span>
          </div>

          {/* CTA buttons */}
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={() => navigate('/consumer/cart')} style={{ flex: 1, padding: '13px', background: '#166534', border: 'none', borderRadius: 10, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: 'white', cursor: 'pointer' }}>Add to Cart</button>
            <button onClick={() => navigate('/consumer/cart')} style={{ flex: 1, padding: '13px', background: 'white', border: '1.5px solid #166534', borderRadius: 10, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#166534', cursor: 'pointer' }}>Buy Now</button>
          </div>
          <button onClick={() => setWished(v => !v)}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, width: '100%', padding: '11px', background: 'white', border: '1.5px solid #e5e7eb', borderRadius: 10, fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: wished ? '#dc2626' : '#374151', cursor: 'pointer' }}>
            <Heart size={16} fill={wished ? '#dc2626' : 'none'} color={wished ? '#dc2626' : '#9ca3af'} />
            {wished ? 'Saved to Favourites' : 'Add to Favourites'}
          </button>
        </div>
      </div>

      {/* Similar Products */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: '#111827' }}>Similar Products</div>
          <button onClick={() => navigate('/consumer/marketplace')} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>View All <ChevronRight size={14} /></button>
        </div>
        <div style={{ display: 'flex', gap: 14 }}>
          {similarItems.map(s => (
            <button key={s.id} onClick={() => { navigate('/consumer/marketplace/' + s.id); setSelectedImg(0); }}
              style={{ flex: 1, background: 'white', border: '1px solid #e7f0eb', borderRadius: 12, padding: '12px 10px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, cursor: 'pointer', textAlign: 'center' }}>
              <div style={{ width: 64, height: 64, borderRadius: 10, overflow: 'hidden', background: '#f9fafb' }}>
                <img src={s.image} alt={s.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#111827' }}>{s.name}</div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#166534', fontWeight: 700 }}>₹{s.price}/{s.unit}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
