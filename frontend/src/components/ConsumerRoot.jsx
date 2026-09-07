import { useState, useRef, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router'
import { Avatar } from './Avatar'
import { X } from 'lucide-react'
import { AgriLogo } from './AgriLogo'
import { LayoutDashboard, Store, ShoppingCart, Package, Truck, Bell, ChevronDown, Mail, Phone, User, LogOut } from 'lucide-react'
import { CONSUMER } from '../data/consumerData'

const NAV = [
  { icon: LayoutDashboard, label: 'Dashboard',    path: '/consumer'               },
  { icon: Store,           label: 'Marketplace',  path: '/consumer/marketplace'   },
  { icon: ShoppingCart,    label: 'Cart',         path: '/consumer/cart'          },
  { icon: Package,         label: 'My Orders',    path: '/consumer/orders'        },
  { icon: Truck,           label: 'Track Order',  path: '/consumer/tracking'      },
  { icon: User,            label: 'Profile',      path: '/consumer/profile'       },
]

export default function ConsumerRoot() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [logoutOpen,   setLogoutOpen]   = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    function h(e) { if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setDropdownOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  function isActive(p) { return p === '/consumer' ? location.pathname === '/consumer' : location.pathname.startsWith(p) }

  return (
    <div style={{ display: 'flex', height: '100%', fontFamily: 'var(--agri-font)', background: 'var(--agri-bg)' }}>
      {/* ── Sidebar: Matches Farmer design & theme ── */}
      <aside style={{ width: 220, minWidth: 220, height: '100%', flexShrink: 0, background: 'var(--agri-sidebar-bg)', display: 'flex', flexDirection: 'column' }}>
        {/* Logo */}
        <div style={{ padding: '20px 18px 16px', display: 'flex', alignItems: 'center', gap: 9 }}>
          <AgriLogo />
          <span style={{ color: 'white', fontFamily: 'var(--agri-font)', fontWeight: 700, fontSize: 19, letterSpacing: '-0.01em' }}>AgriConnect</span>
        </div>
        {/* Nav */}
        <nav style={{ padding: '4px 10px', flex: 1 }}>
          {NAV.map(({ icon: Icon, label, path }) => {
            const active = isActive(path)
            return (
              <button key={label} onClick={() => navigate(path)}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                  padding: '10px 12px',
                  borderRadius: 8, border: 'none', cursor: 'pointer',
                  background: active ? 'var(--agri-sidebar-active)' : 'transparent',
                  color: active ? '#ffffff' : 'rgba(255,255,255,0.72)',
                  fontFamily: 'var(--agri-font)', fontSize: 15,
                  fontWeight: active ? 600 : 400,
                  marginBottom: 2, textAlign: 'left',
                }}>
                <Icon size={18} strokeWidth={2} />
                {label}
              </button>
            )
          })}
        </nav>
      </aside>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <header style={{ height: 56, background: 'white', borderBottom: '1px solid var(--agri-border)', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', padding: '0 24px', gap: 14, flexShrink: 0 }}>
          <button style={{ position: 'relative', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--agri-text-secondary)', display: 'flex', alignItems: 'center', padding: 4 }}>
            <Bell size={19} strokeWidth={1.5}/>
          </button>
          <div ref={dropdownRef} style={{ position: 'relative' }}>
            <button onClick={() => setDropdownOpen(v => !v)} style={{ display: 'flex', alignItems: 'center', gap: 9, background: 'none', border: 'none', cursor: 'pointer', padding: '4px 6px', borderRadius: 'var(--agri-radius-md)' }}>
              <Avatar type="image" src={CONSUMER.avatar} size="medium" shape="circle"/>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)', lineHeight: 1.2 }}>{CONSUMER.name}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)', lineHeight: 1.3 }}>Consumer</div>
              </div>
              <ChevronDown size={13} color="var(--agri-text-secondary)"/>
            </button>
            {dropdownOpen && (
              <div style={{ position: 'absolute', top: 'calc(100% + 6px)', right: 0, width: 200, background: 'white', border: '1px solid var(--agri-border)', borderRadius: 'var(--agri-radius-lg)', boxShadow: '0 4px 16px rgba(0,0,0,0.1)', zIndex: 100, overflow: 'hidden' }}>
                <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--agri-border)' }}>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)' }}>{CONSUMER.name}</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)' }}>{CONSUMER.email}</div>
                </div>
                <div style={{ padding: '6px 8px' }}>
                  <button onClick={() => { setDropdownOpen(false); setLogoutOpen(true) }}
                    style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', border: 'none', background: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-error)', textAlign: 'left' }}>
                    <LogOut size={14} color="var(--agri-error)"/> Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </header>
        <main style={{ flex: 1, overflowY: 'auto' }}><Outlet/></main>
      </div>

      {logoutOpen && (
        <div onClick={e => { if (e.target === e.currentTarget) setLogoutOpen(false) }}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#ffffff', borderRadius: 12, width: 400, boxShadow: '0 20px 60px rgba(0,0,0,0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 20px 0' }}>
              <h2 style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Confirm Logout</h2>
              <button onClick={() => setLogoutOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--agri-text-muted)', display: 'flex' }}><X size={16} /></button>
            </div>
            <div style={{ padding: '14px 20px' }}>
              <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: 0 }}>Are you sure you want to logout?</p>
            </div>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', padding: '0 20px 18px' }}>
              <button onClick={() => setLogoutOpen(false)} style={{ padding: '8px 18px', border: '1px solid var(--agri-border)', borderRadius: 8, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: 'var(--agri-text)', cursor: 'pointer' }}>Cancel</button>
              <button onClick={() => { setLogoutOpen(false); navigate('/') }} style={{ padding: '8px 18px', border: 'none', borderRadius: 8, background: 'var(--agri-primary)', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: '#ffffff', cursor: 'pointer' }}>Logout</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
