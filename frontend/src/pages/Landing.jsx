import { useNavigate } from 'react-router'
import { Sprout, Tag, ShieldCheck, Globe } from 'lucide-react'
import heroImg from '../imports/image-removebg-preview.png'
import { AgriLogo } from '../components/AgriLogo'

/* ── Leaf SVG decoration ─────────────────────────────────────── */
function LeafDecor({ style }) {
  return (
    <svg viewBox="0 0 120 160" fill="none" style={style}>
      <path d="M60 150 C60 150 10 120 8 70 C6 30 30 5 50 20 C50 20 70 60 60 150Z" fill="#DCFCE7" opacity="0.7" />
      <path d="M50 20 C45 70 55 110 60 150" stroke="#86EFAC" strokeWidth="2" fill="none" opacity="0.5" />
    </svg>
  )
}


const FEATURES = [
  {
    icon: <Sprout size={28} strokeWidth={1.8} />,
    title: 'Direct from Farmers',
    desc: 'Support local farmers and get fresh produce.',
  },
  {
    icon: <Tag size={28} strokeWidth={1.8} />,
    title: 'Fair Pricing',
    desc: 'Transparent and competitive pricing.',
  },
  {
    icon: <ShieldCheck size={28} strokeWidth={1.8} />,
    title: 'Quality Assurance',
    desc: 'Verified farmers and quality checks.',
  },
  {
    icon: <Globe size={28} strokeWidth={1.8} />,
    title: 'Sustainable Future',
    desc: 'Better for farmers, consumers and the planet.',
  },
]

const AVATAR_COLORS = ['#d97706', '#16a34a', '#2563eb']

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div style={{ fontFamily: 'var(--agri-font)', minHeight: '100vh', background: '#f0fdf8', position: 'relative', overflowX: 'hidden' }}>

      {/* ── Background leaf decorations ─────────────────────────── */}
      <LeafDecor style={{ position: 'absolute', left: -20, top: 120, width: 110, opacity: 0.5, pointerEvents: 'none' }} />
      <LeafDecor style={{ position: 'absolute', left: -10, top: 220, width: 80, opacity: 0.35, transform: 'rotate(18deg)', pointerEvents: 'none' }} />
      <LeafDecor style={{ position: 'absolute', right: -20, bottom: 80, width: 120, opacity: 0.45, transform: 'scaleX(-1) rotate(-15deg)', pointerEvents: 'none' }} />
      <LeafDecor style={{ position: 'absolute', right: 40, bottom: 0, width: 90, opacity: 0.3, transform: 'scaleX(-1)', pointerEvents: 'none' }} />

      {/* ── Wavy bottom strip ───────────────────────────────────── */}
      <svg viewBox="0 0 1440 80" preserveAspectRatio="none" style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', height: 80, pointerEvents: 'none' }}>
        <path d="M0 40 Q360 80 720 40 Q1080 0 1440 40 L1440 80 L0 80 Z" fill="#dcfce7" opacity="0.55" />
      </svg>

      {/* ── Navbar ──────────────────────────────────────────────── */}
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 60px', height: 72, background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(8px)', borderBottom: '1px solid #e7f5ec', position: 'relative', zIndex: 10 }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <AgriLogo size={72} badgeBg="rgba(255,255,255,0.15)" />
          <div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 28, fontWeight: 800, color: '#14532d', letterSpacing: '-0.02em', lineHeight: 1.1 }}>AgriConnect</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#4b7c5e', letterSpacing: '0.02em' }}>Farmers · Consumers · A Sustainable Future</div>
          </div>
        </div>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 36 }}>
          {['Home', 'About', 'Features', 'Contact'].map((item, i) => (
            <a key={item} href="#" style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: i === 0 ? 600 : 400, color: i === 0 ? '#166534' : '#374151', textDecoration: 'none', borderBottom: i === 0 ? '2px solid #22c55e' : 'none', paddingBottom: i === 0 ? 2 : 0 }}>
              {item}
            </a>
          ))}
        </div>

        {/* CTA buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button onClick={() => navigate('/admin/login')} style={{ padding: '9px 16px', border: '1px solid #d1fae5', borderRadius: 8, background: '#f0fdf4', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>
            Admin Portal
          </button>
          <button onClick={() => navigate('/login')} style={{ padding: '10px 24px', border: '2px solid #166534', borderRadius: 8, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#166534', cursor: 'pointer' }}>
            Login
          </button>
          <button onClick={() => navigate('/register')} style={{ padding: '10px 24px', border: '2px solid #166534', borderRadius: 8, background: '#166534', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'white', cursor: 'pointer' }}>
            Register
          </button>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────── */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', alignItems: 'center', padding: '64px 60px 40px', gap: 0, maxWidth: 1400, margin: '0 auto', position: 'relative', zIndex: 2 }}>

        {/* Left — content */}
        <div style={{ paddingRight: 40 }}>
          {/* Eyebrow */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 12, fontWeight: 700, color: '#16a34a', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Fresher Farms</span>
            <span style={{ width: 4, height: 4, borderRadius: '50%', background: '#86efac' }} />
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 12, fontWeight: 700, color: '#16a34a', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Stronger Communities</span>
          </div>

          {/* Headline */}
          <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 58, fontWeight: 900, lineHeight: 1.08, color: '#111827', margin: '0 0 20px', letterSpacing: '-0.03em' }}>
            Connecting{' '}
            <span style={{ color: '#166534' }}>Farmers</span>
            <br />
            with{' '}
            <span style={{ color: '#22c55e' }}>Consumers</span>
          </h1>

          {/* Subtext */}
          <p style={{ fontFamily: 'var(--agri-font)', fontSize: 18, color: '#4b5563', lineHeight: 1.6, margin: '0 0 36px', maxWidth: 420 }}>
            Fresh, quality produce. Fair prices. A sustainable future for agriculture.
          </p>

          {/* CTAs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 40 }}>
            <button onClick={() => navigate('/login')} className="agri-cta-btn" style={{ padding: '14px 28px', fontSize: 16 }}>
              <svg viewBox="0 0 24 24" className="arr-2" xmlns="http://www.w3.org/2000/svg"><path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z" /></svg>
              <span className="btn-text">Get Started</span>
              <span className="circle" />
              <svg viewBox="0 0 24 24" className="arr-1" xmlns="http://www.w3.org/2000/svg"><path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z" /></svg>
            </button>
          </div>

          {/* Social proof */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ display: 'flex' }}>
              {AVATAR_COLORS.map((bg, i) => (
                <div key={i} style={{ width: 38, height: 38, borderRadius: '50%', border: '2.5px solid white', background: bg, marginLeft: i === 0 ? 0 : -10, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 700 }}>
                  {['R', 'P', 'A'][i]}
                </div>
              ))}
            </div>
            <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#4b5563', margin: 0, lineHeight: 1.4 }}>
              <strong style={{ color: '#111827' }}>Trusted by 10,000+</strong> farmers<br />and consumers across India
            </p>
          </div>
        </div>

        {/* Right — hero image, white bg removed via multiply blend */}
        <div style={{ position: 'relative', overflow: 'visible' }}>
          <img
            src={heroImg}
            alt="Farmer standing in a lush green field at sunset"
            style={{
              width: '130%',
              maxWidth: 'none',
              display: 'block',
              marginLeft: '-25%',
              marginTop: -40,
            }}
          />
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────────── */}
      <section style={{ padding: '20px 60px 100px', maxWidth: 1400, margin: '0 auto', position: 'relative', zIndex: 2 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 1, border: '1px solid #e7f5ec', borderRadius: 16, overflow: 'hidden', background: '#e7f5ec' }}>
          {FEATURES.map(({ icon, title, desc }, i) => (
            <div key={i} style={{ background: 'white', padding: '32px 28px 36px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 0 }}>
              {/* Icon badge */}
              <div style={{ width: 64, height: 64, borderRadius: 14, background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16a34a', marginBottom: 18 }}>
                {icon}
              </div>
              <h3 style={{ fontFamily: 'var(--agri-font)', fontSize: 18, fontWeight: 800, color: '#111827', margin: '0 0 10px', letterSpacing: '-0.01em' }}>{title}</h3>
              <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', lineHeight: 1.55, margin: 0 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer strip ────────────────────────────────────────── */}
      <div style={{ textAlign: 'center', paddingBottom: 40, position: 'relative', zIndex: 2 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, marginBottom: 10 }}>
          <div style={{ height: 1, width: 120, background: '#d1fae5' }} />
          <AgriLogo size={44} badgeBg="rgba(255,255,255,0.15)" />
          <div style={{ height: 1, width: 120, background: '#d1fae5' }} />
        </div>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', margin: '0 0 8px' }}>
          Good Food · Stronger Farmers · Healthier Communities
        </p>
        <button onClick={() => navigate('/admin/login')} style={{ background: 'none', border: 'none', fontSize: 13, color: '#166534', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline', fontFamily: 'var(--agri-font)' }}>
          Admin Login (admin@123)
        </button>
      </div>

    </div>
  )
}
