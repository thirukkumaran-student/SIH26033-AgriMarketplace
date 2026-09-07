import { useState } from 'react'
import { User, MapPin, CreditCard, Settings, Bell, Shield, Edit, Sprout } from 'lucide-react'
import { CONSUMER } from '../data/consumerData'

const SECTIONS = [
  { label: 'Profile Information', icon: User         },
  { label: 'Addresses',           icon: MapPin       },
  { label: 'Payment Methods',     icon: CreditCard   },
  { label: 'Preferences',         icon: Settings     },
  { label: 'Notifications',       icon: Bell         },
  { label: 'Security',            icon: Shield       },
]

export default function ConsumerProfile() {
  const [section, setSection] = useState('Profile Information')
  const c = CONSUMER

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, padding: '24px 32px' }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>My Profile</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Manage your account information.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: 20 }}>
        {/* Left nav */}
        <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '10px', alignSelf: 'start' }}>
          {SECTIONS.map(({ label, icon: Icon }) => (
            <button key={label} onClick={() => setSection(label)}
              style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 11, padding: '11px 12px', borderRadius: 9, border: 'none', background: section === label ? '#f0fdf4' : 'transparent', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: section === label ? 600 : 400, color: section === label ? '#166534' : '#374151', cursor: 'pointer', marginBottom: 2, textAlign: 'left' }}>
              <Icon size={16} color={section === label ? '#166534' : '#9ca3af'} />
              {label}
            </button>
          ))}
        </div>

        {/* Right content */}
        <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px', borderBottom: '1px solid #f3f4f6' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: '#111827' }}>{section}</div>
            {section === 'Profile Information' && (
              <button style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', borderRadius: 8, border: '1.5px solid #e5e7eb', background: 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: '#374151', cursor: 'pointer' }}>
                <Edit size={14} /> Edit
              </button>
            )}
          </div>

          {section === 'Profile Information' ? (
            <div style={{ padding: '24px' }}>
              {/* Avatar */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginBottom: 28 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 84, height: 84, borderRadius: '50%', overflow: 'hidden', border: '3px solid #bbf7d0', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
                    <img src={c.avatar} alt={c.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  </div>
                  <button style={{ padding: '5px 14px', borderRadius: 8, border: '1.5px solid #e5e7eb', background: 'white', fontFamily: 'var(--agri-font)', fontSize: 13, fontWeight: 500, color: '#374151', cursor: 'pointer' }}>Change Photo</button>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 20, fontWeight: 800, color: '#111827', marginBottom: 4 }}>{c.name}</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>{c.email}</div>
                  <div style={{ display: 'inline-block', marginTop: 8, fontFamily: 'var(--agri-font)', fontSize: 12, fontWeight: 600, color: '#166534', background: '#dcfce7', padding: '3px 10px', borderRadius: 12 }}>Verified Consumer</div>
                </div>
              </div>

              {/* Fields grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                {[
                  ['Full Name',     c.name],
                  ['Email Address', c.email],
                  ['Phone Number',  c.phone],
                  ['Location',      c.location],
                  ['Member Since',  c.memberSince],
                ].map(([label, val]) => (
                  <div key={label}>
                    <div style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>{label}</div>
                    <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151', background: '#f9fafb', border: '1.5px solid #e5e7eb', borderRadius: 9, padding: '10px 14px' }}>{val}</div>
                  </div>
                ))}
              </div>

              {/* Footer banner */}
              <div style={{ marginTop: 28, borderRadius: 12, background: 'linear-gradient(135deg, #dcfce7, #f0fdf4)', border: '1px solid #bbf7d0', padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: '#166534' }}>Together for a sustainable tomorrow</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', marginTop: 2 }}>Support local farmers. Choose fresh. Choose AgriConnect.</div>
                </div>
                <div style={{ width: 44, height: 44, borderRadius: '50%', background: '#bbf7d0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sprout size={24} color="#166534" />
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '60px 40px', textAlign: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, color: '#9ca3af' }}>
              {section} — coming soon
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
