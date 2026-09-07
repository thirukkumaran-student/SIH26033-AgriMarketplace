import { useState, useRef, useEffect } from 'react'
import { AgriLogo } from './AgriLogo'
import { Outlet, useNavigate, useLocation } from 'react-router'
import { Avatar } from './Avatar'
import { X } from 'lucide-react'
import {
  LayoutDashboard, Package, ShoppingCart, ShieldCheck, Truck,
  TrendingUp, User, Settings, Bell, ChevronDown, Mail, Phone, LogOut,
} from 'lucide-react'
import { FARMER } from '../data'

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard',    path: '/dashboard'             },
  { icon: Package,         label: 'My Produce',   path: '/produce'      },
  { icon: ShoppingCart,    label: 'Orders',       path: '/orders'       },
  { icon: ShieldCheck,     label: 'Verification', path: '/verification' },
  { icon: Truck,           label: 'Shipments',    path: '/shipments'    },
  { icon: TrendingUp,      label: 'Forecasts',    path: '/forecasts'    },
  { icon: User,            label: 'Profile',      path: '/profile'      },
  { icon: Settings,        label: 'Settings',     path: '/settings'     },
]


export default function Root() {
  const navigate    = useNavigate()
  const location    = useLocation()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [logoutOpen,   setLogoutOpen]   = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    function h(e) { if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setDropdownOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  function isActive(path) {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/dashboard/'
    }
    return location.pathname === path || location.pathname.startsWith(path + '/') ||
           location.pathname === `/dashboard${path}` || location.pathname.startsWith(`/dashboard${path}/`)
  }

  return (
    <div style={{ display: 'flex', height: '100%', fontFamily: 'var(--agri-font)', background: 'var(--agri-bg)' }}>

      {/* ── Sidebar ─────────────────────────────────────────────────────
          Custom sidebar: SidebarNavigation is a fixed 60px icon-only rail with
          surface-bg background; this design requires ~200px wide sidebar with
          text labels on a dark #166534 green background.
      ── */}
      <aside style={{ width: 220, minWidth: 220, height: '100%', flexShrink: 0, background: 'var(--agri-sidebar-bg)', display: 'flex', flexDirection: 'column' }}>
        {/* Logo */}
        <div style={{ padding: '20px 18px 16px', display: 'flex', alignItems: 'center', gap: 9 }}>
          <AgriLogo />
          <span style={{ color: 'white', fontFamily: 'var(--agri-font)', fontWeight: 700, fontSize: 19, letterSpacing: '-0.01em' }}>AgriConnect</span>
        </div>
        {/* Nav */}
        <nav style={{ padding: '4px 10px', flex: 1 }}>
          {NAV_ITEMS.map(({ icon: Icon, label, path }) => {
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

      {/* Main */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopBar dropdownRef={dropdownRef} dropdownOpen={dropdownOpen}
          setDropdownOpen={setDropdownOpen} setLogoutOpen={setLogoutOpen} navigate={navigate} />
        <main style={{ flex: 1, overflowY: 'auto' }}>
          <Outlet />
        </main>
      </div>

      {logoutOpen && (
        <div onClick={e => { if (e.target === e.currentTarget) setLogoutOpen(false) }}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#ffffff', borderRadius: 12, width: 400, boxShadow: '0 20px 60px rgba(0,0,0,0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 20px 0' }}>
              <h2 style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Confirm Logout</h2>
              <button onClick={() => setLogoutOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--agri-text-muted)', display: 'flex' }}>
                <X size={16} />
              </button>
            </div>
            <div style={{ padding: '14px 20px' }}>
              <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: 0 }}>
                Are you sure you want to logout?
              </p>
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

export function TopBar({ dropdownRef, dropdownOpen, setDropdownOpen, setLogoutOpen, navigate }) {
  return (
    <header style={{ height: 64, background: 'white', borderBottom: '1px solid var(--agri-border)', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', padding: '0 24px', gap: 16, flexShrink: 0 }}>
      <button style={{ position: 'relative', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--agri-text-secondary)', display: 'flex', alignItems: 'center', padding: 6 }}>
        <Bell size={22} strokeWidth={2} />
        <span style={{ position: 'absolute', top: 4, right: 4, width: 8, height: 8, borderRadius: '50%', background: 'var(--agri-error)', border: '2px solid white' }} />
      </button>

      <div ref={dropdownRef} style={{ position: 'relative' }}>
        <button onClick={() => setDropdownOpen(v => !v)}
          style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'none', border: 'none', cursor: 'pointer', padding: '4px 6px', borderRadius: 8 }}>
          <Avatar type="image" src={FARMER.avatar} size="large" shape="circle" />
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'var(--agri-text)', lineHeight: 1.2 }}>{FARMER.name}</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', lineHeight: 1.3 }}>{FARMER.role}</div>
          </div>
          <ChevronDown size={15} color="var(--agri-text-secondary)"
            style={{ transform: dropdownOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s' }} />
        </button>

        {dropdownOpen && (
          <div style={{ position: 'absolute', top: 'calc(100% + 6px)', right: 0, width: 240, background: 'white', border: '1px solid var(--agri-border)', borderRadius: 8, boxShadow: '0 4px 16px rgba(0,0,0,0.10)', zIndex: 200, overflow: 'hidden' }}>
            <div style={{ padding: '14px 16px 12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <Avatar type="image" src={FARMER.avatar} size="medium" shape="circle" />
                <div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)' }}>{FARMER.name}</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)' }}>{FARMER.role}</div>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                  <Mail size={12} color="var(--agri-text-muted)" />
                  <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)' }}>{FARMER.email}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                  <Phone size={12} color="var(--agri-text-muted)" />
                  <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)' }}>{FARMER.phone}</span>
                </div>
              </div>
            </div>
            <div style={{ height: 1, background: 'var(--agri-border)' }} />
            <div style={{ padding: '6px 8px' }}>
              <DropdownItem label="Profile"  icon={<User size={14} color="var(--agri-text-secondary)" />} onClick={() => { setDropdownOpen(false); navigate('/profile') }} />
              <DropdownItem label="Logout"   icon={<LogOut size={14} color="var(--agri-error)" />}        onClick={() => { setDropdownOpen(false); setLogoutOpen(true) }} danger />
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

function DropdownItem({ label, icon, onClick, danger }) {
  return (
    <button onClick={onClick} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', borderRadius: 4, border: 'none', background: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 15, color: danger ? 'var(--agri-error)' : 'var(--agri-text)', textAlign: 'left' }}>
      {icon} {label}
    </button>
  )
}

