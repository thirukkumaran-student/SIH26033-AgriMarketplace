import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Trash2, Plus, Minus, ArrowRight, ShoppingBag, ShieldCheck, ArrowLeft, Truck } from 'lucide-react'

export default function ConsumerCart() {
  const navigate = useNavigate()
  const [items, setItems] = useState([
    {
      id: 1,
      name: 'Farm Fresh Tomatoes',
      farmer: 'Ravi Kumar',
      qty: 5,
      unit: 'kg',
      price: 25,
      image: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=300&h=300&fit=crop&q=80',
    },
    {
      id: 2,
      name: 'Ponni Raw Rice (Grade A)',
      farmer: 'Suresh',
      qty: 10,
      unit: 'kg',
      price: 45,
      image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300&h=300&fit=crop&q=80',
    },
    {
      id: 3,
      name: 'Alphonso Mangoes',
      farmer: 'Priya Kumar',
      qty: 3,
      unit: 'kg',
      price: 80,
      image: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=300&fit=crop&q=80',
    },
  ])
  const [checkedOut, setCheckedOut] = useState(false)

  function updateQty(id, delta) {
    setItems(prev =>
      prev.map(item => {
        if (item.id === id) {
          const newQty = Math.max(1, item.qty + delta)
          return { ...item, qty: newQty }
        }
        return item
      })
    )
  }

  function removeItem(id) {
    setItems(prev => prev.filter(item => item.id !== id))
  }

  const subtotal = items.reduce((sum, item) => sum + item.qty * item.price, 0)
  const deliveryFee = items.length > 0 ? 30 : 0
  const platformFee = items.length > 0 ? 10 : 0
  const total = subtotal + deliveryFee + platformFee

  function handleCheckout() {
    setCheckedOut(true)
    setTimeout(() => {
      navigate('/consumer/tracking')
    }, 1500)
  }

  if (checkedOut) {
    return (
      <div style={{ padding: '60px 24px', textAlign: 'center', fontFamily: 'var(--agri-font)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{ width: 72, height: 72, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16a34a' }}>
          <ShieldCheck size={42} />
        </div>
        <h2 style={{ fontSize: 26, fontWeight: 900, color: '#111827', margin: 0 }}>Order Placed with Farmers!</h2>
        <p style={{ fontSize: 15, color: '#4b5563', margin: 0, maxWidth: 440 }}>
          Your order notification has been sent directly to Ravi Kumar, Suresh, and Priya Kumar. Connecting you to live tracking...
        </p>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 24, fontFamily: 'var(--agri-font)' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>My Shopping Cart</h1>
          <p style={{ fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Review your direct-from-farm produce before ordering</p>
        </div>

        <button
          onClick={() => navigate('/consumer/marketplace')}
          style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'white', border: '1px solid #e5e7eb', padding: '9px 16px', borderRadius: 8, fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}
        >
          <ArrowLeft size={15} /> Continue Shopping
        </button>
      </div>

      {items.length === 0 ? (
        <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 16, padding: '60px 24px', textAlign: 'center' }}>
          <ShoppingBag size={52} color="#9ca3af" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: 20, fontWeight: 800, color: '#111827', margin: '0 0 6px' }}>Your Cart is Empty</h3>
          <p style={{ fontSize: 15, color: '#6b7280', margin: '0 0 24px' }}>Discover fresh organic produce directly from verified farmers in your district.</p>
          <button
            onClick={() => navigate('/consumer/marketplace')}
            style={{ padding: '12px 28px', background: '#166534', color: 'white', border: 'none', borderRadius: 10, fontSize: 15, fontWeight: 700, cursor: 'pointer' }}
          >
            Explore Fresh Harvest →
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1.9fr 1fr', gap: 24, alignItems: 'start' }}>

          {/* Cart items list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {items.map(item => (
              <div
                key={item.id}
                style={{
                  background: 'white',
                  border: '1px solid #e7f0eb',
                  borderRadius: 14,
                  padding: '18px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 18,
                  boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                }}
              >
                <img
                  src={item.image}
                  alt={item.name}
                  style={{ width: 80, height: 80, borderRadius: 12, objectFit: 'cover', border: '1px solid #edf2ef' }}
                />

                <div style={{ flex: 1 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: '0 0 4px' }}>{item.name}</h3>
                  <div style={{ fontSize: 13, color: '#6b7280' }}>Harvested by <strong>{item.farmer}</strong></div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: '#166534', marginTop: 4 }}>
                    ₹{item.price} / {item.unit}
                  </div>
                </div>

                {/* Qty */}
                <div style={{ display: 'flex', alignItems: 'center', border: '1.5px solid #e5e7eb', borderRadius: 8, padding: '4px 6px', background: '#f9fafb' }}>
                  <button onClick={() => updateQty(item.id, -1)} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', color: '#6b7280', padding: 4 }}>
                    <Minus size={14} />
                  </button>
                  <span style={{ fontSize: 14, fontWeight: 700, minWidth: 28, textAlign: 'center', color: '#111827' }}>{item.qty}</span>
                  <button onClick={() => updateQty(item.id, 1)} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', color: '#6b7280', padding: 4 }}>
                    <Plus size={14} />
                  </button>
                </div>

                <div style={{ fontSize: 17, fontWeight: 800, color: '#111827', minWidth: 75, textAlign: 'right' }}>
                  ₹{item.qty * item.price}
                </div>

                <button
                  onClick={() => removeItem(item.id)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#dc2626', padding: 6, display: 'flex' }}
                  title="Remove"
                >
                  <Trash2 size={17} />
                </button>
              </div>
            ))}

            <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 12, padding: '12px 18px', color: '#166534', fontSize: 13, fontWeight: 600 }}>
              <Truck size={18} /> Direct refrigerated delivery ensures your vegetables & fruits stay crisp and vitamin-rich.
            </div>
          </div>

          {/* Order Summary */}
          <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 16, padding: '24px', display: 'flex', flexDirection: 'column', gap: 18, boxShadow: '0 2px 10px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#111827', margin: 0 }}>Order Summary</h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontSize: 14, color: '#4b5563' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Produce Total</span>
                <span style={{ fontWeight: 700, color: '#111827' }}>₹{subtotal}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>FastTrack Farm Delivery</span>
                <span style={{ fontWeight: 700, color: '#111827' }}>₹{deliveryFee}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Platform Quality Inspection</span>
                <span style={{ fontWeight: 700, color: '#111827' }}>₹{platformFee}</span>
              </div>

              <div style={{ height: 1, background: '#e5e7eb', margin: '4px 0' }} />

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 18, fontWeight: 900, color: '#111827' }}>
                <span>Final Amount</span>
                <span style={{ color: '#166534' }}>₹{total}</span>
              </div>
            </div>

            <button
              onClick={handleCheckout}
              style={{
                width: '100%',
                padding: '14px',
                background: '#166534',
                color: 'white',
                border: 'none',
                borderRadius: 10,
                fontSize: 15,
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                boxShadow: '0 4px 14px rgba(22, 101, 52, 0.25)',
              }}
            >
              Confirm & Place Order <ArrowRight size={17} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: 12, color: '#6b7280' }}>
              <ShieldCheck size={14} color="#166534" /> 100% Secure Payment & Quality Guarantee
            </div>
          </div>

        </div>
      )}

    </div>
  )
}
