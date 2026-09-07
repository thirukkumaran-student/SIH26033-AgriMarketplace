import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Mail, Lock, Eye, EyeOff, Phone, ChevronDown } from 'lucide-react'
import { AgriLogo } from '../components/AgriLogo'
import farmImg from '../imports/regis.png'
import bgImg from '../imports/bg-1.png'

const ROLES = ['FARMER', 'CONSUMER', 'ADMIN', 'BULK_BUYER', 'FINANCIER', 'LOGISTICS']
const ROLE_LABELS = {
  FARMER: 'Farmer',
  CONSUMER: 'Consumer',
  ADMIN: 'Admin (Portal)',
  BULK_BUYER: 'Bulk Buyer',
  FINANCIER: 'Financier',
  LOGISTICS: 'Logistics',
}

export default function Login() {
  const navigate = useNavigate()
  const [role, setRole] = useState('FARMER')
  const [roleOpen, setRoleOpen] = useState(false)
  const [identifier, setIdentifier] = useState('ravi@example.com')
  const [password, setPassword] = useState('password123')
  const [showPass, setShowPass] = useState(false)
  const [remember, setRemember] = useState(false)
  const [error, setError] = useState('')

  const isFarmer = role === 'FARMER'

  function handleRoleChange(newRole) {
    setRole(newRole)
    setRoleOpen(false)
    // Populate sensible demo defaults based on role
    if (newRole === 'FARMER') {
      setIdentifier('+91 98765 43210')
      setPassword('farmer@123')
    } else if (newRole === 'CONSUMER') {
      setIdentifier('ananya@example.com')
      setPassword('consumer@123')
    } else if (newRole === 'ADMIN') {
      setIdentifier('admin@123')
      setPassword('admin@123')
    } else {
      setIdentifier('buyer@example.com')
      setPassword('password123')
    }
  }

  function handleLogin(e) {
    e?.preventDefault?.()
    setError('')

    const cleanId = identifier.trim()
    const cleanPass = password.trim()

    if (!cleanId || !cleanPass) {
      setError('Please enter your credentials to login')
      return
    }

    // Role-based direct navigation
    if (role === 'ADMIN' || cleanId.toLowerCase() === 'admin' || cleanId.toLowerCase() === 'admin@123') {
      navigate('/admin')
      return
    }

    if (role === 'CONSUMER') {
      navigate('/consumer')
      return
    }

    // Default to Farmer module
    navigate('/dashboard')
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundImage: `url(${bgImg})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'var(--agri-font)', padding: 24,
      position: 'relative',
    }}>
      {/* Subtle dark overlay so card pops */}
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.35)' }} />

      {/* Card */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', width: '100%', maxWidth: 820, borderRadius: 24, overflow: 'hidden', boxShadow: '0 24px 80px rgba(0,0,0,0.25)', background: 'white' }}>

        {/* ── Left: form ─────────────────────────────────────────── */}
        <div style={{ flex: 1, padding: '44px 48px', display: 'flex', flexDirection: 'column' }}>

          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28, cursor: 'pointer' }} onClick={() => navigate('/')}>
            <AgriLogo size={60} badgeBg="#f0fdf4" />
            <div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 26, fontWeight: 800, color: '#14532d', letterSpacing: '-0.02em', lineHeight: 1.1 }}>AgriConnect</div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#4b7c5e' }}>Farmers · Consumers · A Sustainable Future</div>
            </div>
          </div>

          <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 34, fontWeight: 900, color: '#111827', margin: '0 0 8px', letterSpacing: '-0.02em' }}>
            Welcome <span style={{ color: '#166534' }}>Back</span>
          </h1>
          <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '0 0 20px' }}>
            Select your role and login to continue to your account
          </p>

          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '10px 14px', marginBottom: 14, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#dc2626' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} noValidate style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 14 }}>

              {/* Role dropdown */}
              <RoleDropdown role={role} onSelectRole={handleRoleChange} roleOpen={roleOpen} setRoleOpen={setRoleOpen} />

              {/* Email or Phone or Username */}
              {isFarmer ? (
                <InputField
                  icon={<Phone size={15} color="#9ca3af" />}
                  placeholder="Phone number or Email"
                  type="text"
                  value={identifier}
                  onChange={e => setIdentifier(e.target.value)}
                />
              ) : (
                <InputField
                  icon={<Mail size={15} color="#9ca3af" />}
                  placeholder={role === 'ADMIN' ? 'Admin username / email (admin@123)' : 'Email address or username'}
                  type="text"
                  value={identifier}
                  onChange={e => setIdentifier(e.target.value)}
                />
              )}

              <InputField
                icon={<Lock size={15} color="#9ca3af" />}
                placeholder="Password"
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                suffix={
                  <button type="button" onClick={() => setShowPass(v => !v)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'flex', color: '#9ca3af' }}>
                    {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                }
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151' }}>
                <input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} style={{ width: 15, height: 15, accentColor: '#166534', cursor: 'pointer' }} />
                Remember me
              </label>
              <button type="button" style={{ background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer', padding: 0 }}>
                Forgot password?
              </button>
            </div>

            <button type="submit" style={{ width: '100%', padding: '14px', background: '#166534', border: 'none', borderRadius: 10, fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: 'white', cursor: 'pointer', marginBottom: 16 }}>
              Login to {ROLE_LABELS[role] || 'Module'} →
            </button>
          </form>

          <Divider label="Or continue with" />

          <div style={{ display: 'flex', justifyContent: 'center', margin: '14px 0 18px' }}>
            <GoogleBtn />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center' }}>
            <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', margin: 0 }}>
              Don't have an account?{' '}
              <button onClick={() => navigate('/register')} style={{ background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 700, color: '#166534', cursor: 'pointer', padding: 0 }}>
                Register now
              </button>
            </p>

            <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 600, color: '#4b5563', cursor: 'pointer', padding: 0, textDecoration: 'underline' }}>
              ← Back to Home
            </button>
          </div>
        </div>

        {/* ── Right: image ─────────────────────────────────────────── */}
        <div style={{ width: 300, flexShrink: 0, overflow: 'hidden' }}>
          <img src={farmImg} alt="Farmer with tablet in green field"
            style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center' }} />
        </div>

      </div>
    </div>
  )
}

function RoleDropdown({ role, onSelectRole, roleOpen, setRoleOpen }) {
  return (
    <div style={{ position: 'relative' }}>
      <button type="button" onClick={() => setRoleOpen(v => !v)}
        style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px', border: `1.5px solid ${roleOpen ? '#166534' : '#e5e7eb'}`, borderRadius: 10, background: roleOpen ? '#f0fdf4' : '#fafafa', fontFamily: 'var(--agri-font)', fontSize: 15, color: role ? '#111827' : '#9ca3af', cursor: 'pointer', textAlign: 'left' }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
        <span style={{ flex: 1, fontWeight: 600, color: '#166534' }}>Role: {role ? ROLE_LABELS[role] : 'Select Role'}</span>
        <ChevronDown size={15} color="#9ca3af" style={{ transform: roleOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
      </button>
      {roleOpen && (
        <div style={{ position: 'absolute', top: 'calc(100% + 4px)', left: 0, right: 0, background: 'white', border: '1.5px solid #e5e7eb', borderRadius: 10, boxShadow: '0 8px 24px rgba(0,0,0,0.12)', zIndex: 50, overflow: 'hidden' }}>
          {ROLES.map((r, i) => (
            <button key={r} type="button" onClick={() => onSelectRole(r)}
              style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', background: role === r ? '#f0fdf4' : 'white', border: 'none', fontFamily: 'var(--agri-font)', fontSize: 15, color: role === r ? '#166534' : '#374151', cursor: 'pointer', textAlign: 'left', borderTop: i > 0 ? '1px solid #f3f4f6' : 'none', fontWeight: role === r ? 700 : 400 }}>
              {role === r ? (
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#166534', flexShrink: 0 }} />
              ) : (
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#e5e7eb', flexShrink: 0 }} />
              )}
              {ROLE_LABELS[r]}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function InputField({ icon, placeholder, type = 'text', value, onChange, suffix }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1.5px solid #e5e7eb', borderRadius: 10, padding: '12px 14px', background: '#fafafa' }}>
      {icon}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        style={{ flex: 1, border: 'none', background: 'transparent', fontFamily: 'var(--agri-font)', fontSize: 15, color: '#111827', outline: 'none' }}
      />
      {suffix}
    </div>
  )
}

function Divider({ label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <div style={{ flex: 1, height: 1, background: '#e5e7eb' }} />
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af', whiteSpace: 'nowrap' }}>{label}</span>
      <div style={{ flex: 1, height: 1, background: '#e5e7eb' }} />
    </div>
  )
}

function GoogleBtn() {
  return (
    <button type="button" style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 32px', border: '1.5px solid #e5e7eb', borderRadius: 10, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: '#374151', cursor: 'pointer', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
      <GoogleIcon /> Continue with Google
    </button>
  )
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48">
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.7 2.5 30.2 0 24 0 14.6 0 6.6 5.4 2.6 13.3l7.8 6C12.2 13 17.7 9.5 24 9.5z"/>
      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17z"/>
      <path fill="#FBBC05" d="M10.4 28.7A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.9-4.7l-7.8-6A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.7l7.8-6z"/>
      <path fill="#34A853" d="M24 48c6.2 0 11.4-2 15.2-5.5l-7.5-5.8c-2 1.4-4.6 2.2-7.7 2.2-6.3 0-11.7-4.2-13.6-9.9l-7.8 6C6.6 42.6 14.6 48 24 48z"/>
    </svg>
  )
}
