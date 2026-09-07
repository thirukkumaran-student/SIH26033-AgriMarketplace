import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Mail, Lock, Eye, EyeOff, ArrowLeft } from 'lucide-react'
import { AgriLogo } from '../components/AgriLogo'
import bgImg from '../imports/bg-1.png'
import { ADMIN_CREDENTIALS } from '../data/adminData'

export default function AdminLogin() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  function handleLogin(e) {
    e?.preventDefault?.()
    const cleanEmail = email.trim().toLowerCase()
    const cleanPass = password.trim()
    if (
      (cleanEmail === ADMIN_CREDENTIALS.email.toLowerCase() ||
       cleanEmail === 'admin' ||
       cleanEmail === 'admin@agriconnect.com' ||
       cleanEmail === 'admin@123') &&
      cleanPass === ADMIN_CREDENTIALS.password
    ) {
      navigate('/admin')
    } else {
      setError('Invalid credentials. Use admin@123 / admin@123')
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundImage: `url(${bgImg})`, backgroundSize: 'cover', backgroundPosition: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', padding: 24, position: 'relative' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)' }} />

      <div style={{ position: 'relative', zIndex: 1, width: '100%', maxWidth: 420, background: 'white', borderRadius: 24, padding: '44px 40px', boxShadow: '0 32px 80px rgba(0,0,0,0.3)' }}>
        <button
          type="button"
          onClick={() => navigate('/')}
          style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', cursor: 'pointer', color: '#6b7280', fontSize: 13, fontWeight: 600, padding: 0, marginBottom: 16 }}
        >
          <ArrowLeft size={14} /> Back to Home
        </button>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 28 }}>
          <AgriLogo size={64} badgeBg="#f0fdf4" />
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#14532d', letterSpacing: '-0.02em', marginTop: 12 }}>AgriConnect</div>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#4b7c5e', marginTop: 2 }}>Admin Portal</div>
        </div>

        <h2 style={{ fontFamily: 'var(--agri-font)', fontSize: 26, fontWeight: 900, color: '#111827', margin: '0 0 6px', letterSpacing: '-0.02em' }}>
          Admin <span style={{ color: '#166534' }}>Login</span>
        </h2>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', margin: '0 0 20px' }}>
          Sign in to access the admin dashboard
        </p>

        <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 8, padding: '8px 12px', marginBottom: 16, fontSize: 13, color: '#166534' }}>
          <strong>Default Admin:</strong> <code>admin@123</code> / <code>admin@123</code>
        </div>

        {error && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '10px 14px', marginBottom: 16, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#dc2626' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} noValidate style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <InputField
            icon={<Mail size={15} color="#9ca3af" />}
            placeholder="Admin Email / Username"
            type="text"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
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

          <button type="submit" style={{ width: '100%', marginTop: 6, padding: '14px', background: '#166534', border: 'none', borderRadius: 10, fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: 'white', cursor: 'pointer' }}>
            Sign In →
          </button>
        </form>

        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af', textAlign: 'center', marginTop: 24, marginBottom: 0 }}>
          Authorized personnel only
        </p>
      </div>
    </div>
  )
}

function InputField({ icon, placeholder, type = 'text', value, onChange, suffix }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1.5px solid #e5e7eb', borderRadius: 10, padding: '12px 14px', background: '#fafafa' }}>
      {icon}
      <input type={type} placeholder={placeholder} value={value} onChange={onChange}
        style={{ flex: 1, border: 'none', background: 'transparent', fontFamily: 'var(--agri-font)', fontSize: 15, color: '#111827', outline: 'none' }} />
      {suffix}
    </div>
  )
}
