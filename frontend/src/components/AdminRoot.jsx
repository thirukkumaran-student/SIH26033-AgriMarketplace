import { NavLink, Outlet, useNavigate } from 'react-router'
import { LayoutDashboard, UserCheck, AlertTriangle, Users, ShoppingBag, Package, Activity, Settings, LogOut, Bell, Search } from 'lucide-react'
import { AgriLogo } from './AgriLogo'

const NAV = [
  { to: '/admin',              label: 'Dashboard',          icon: LayoutDashboard, end: true },
  { to: '/admin/verification', label: 'Farmer Verification',icon: UserCheck       },
  { to: '/admin/disputes',     label: 'Disputes',           icon: AlertTriangle   },
  { to: '/admin/users',        label: 'Users',              icon: Users           },
  { to: '/admin/listings',     label: 'Produce / Listings', icon: ShoppingBag     },
  { to: '/admin/orders',       label: 'Orders',             icon: Package         },
  { to: '/admin/monitoring',   label: 'Monitoring',         icon: Activity        },
  { to: '/admin/settings',     label: 'Settings',           icon: Settings        },
]

export default function AdminRoot() {
  const navigate = useNavigate()

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'var(--agri-font)', background: '#f6fdf8' }}>

      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside style={{ width: 230, flexShrink: 0, background: 'var(--agri-sidebar-bg, #14532d)', display: 'flex', flexDirection: 'column', height: '100vh', position: 'sticky', top: 0 }}>
        <div style={{ padding: '22px 18px 18px', display: 'flex', alignItems: 'center', gap: 10, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <AgriLogo size={42} badgeBg="white" />
          <div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 800, color: 'white', letterSpacing: '-0.01em', lineHeight: 1.1 }}>AgriConnect</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 10, color: 'rgba(255,255,255,0.55)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>Admin Panel</div>
          </div>
        </div>

        <nav style={{ flex: 1, padding: '14px 10px', overflowY: 'auto' }}>
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 11, padding: '10px 12px', borderRadius: 9, marginBottom: 2,
                background: isActive ? '#166534' : 'transparent',
                color: isActive ? 'white' : 'rgba(255,255,255,0.65)',
                fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: isActive ? 600 : 400,
                textDecoration: 'none', transition: 'background 0.15s',
              })}>
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: '12px 10px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <button onClick={() => navigate('/')}
            style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 11, padding: '10px 12px', borderRadius: 9, background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.65)', fontFamily: 'var(--agri-font)', fontSize: 15, cursor: 'pointer' }}>
            <LogOut size={17} /> Logout
          </button>
        </div>
      </aside>

      {/* ── Main content ────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <header style={{ height: 60, background: 'white', borderBottom: '1px solid #e7f0eb', display: 'flex', alignItems: 'center', padding: '0 28px', gap: 16, position: 'sticky', top: 0, zIndex: 10, flexShrink: 0 }}>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10, background: '#f6fdf8', border: '1.5px solid #e7f0eb', borderRadius: 10, padding: '8px 14px', maxWidth: 400 }}>
            <Search size={15} color="#9ca3af" />
            <input placeholder="Search farmers, orders, disputes..." style={{ flex: 1, border: 'none', background: 'transparent', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151', outline: 'none' }} />
          </div>

          <div style={{ flex: 1 }} />

          <button style={{ position: 'relative', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 38, height: 38, borderRadius: '50%', color: '#374151' }}>
            <Bell size={20} />
            <span style={{ position: 'absolute', top: 7, right: 8, width: 8, height: 8, borderRadius: '50%', background: '#dc2626', border: '2px solid white' }} />
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#166534', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 700 }}>A</div>
            <div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 700, color: '#111827', lineHeight: 1.2 }}>Admin</div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#6b7280' }}>Super Admin</div>
            </div>
          </div>
        </header>

        <main style={{ flex: 1, padding: '28px 28px 40px', overflowY: 'auto' }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
