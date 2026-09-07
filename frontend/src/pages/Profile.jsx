import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Avatar } from '../components/Avatar'
import { Mail, Phone, MapPin, Lock, LogOut } from 'lucide-react'
import { FARMER } from '../data'
import { GreenBtn } from './Dashboard'

export default function Profile() {
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)
  const [form, setForm]       = useState({ name: FARMER.name, email: FARMER.email, phone: FARMER.phone, location: FARMER.location })

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>My Profile</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>View and manage your account details</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 16 }}>
        {/* Left: Profile Info */}
        <div style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--agri-border)' }}>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)' }}>Profile Information</span>
          </div>
          <div style={{ padding: 20 }}>
            <div style={{ display: 'flex', gap: 18, alignItems: 'flex-start', marginBottom: 20 }}>
              <Avatar type="image" src={FARMER.avatar} size="large" shape="circle" />
              <div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 17, fontWeight: 700, color: 'var(--agri-text)', marginBottom: 2 }}>{FARMER.name}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)', marginBottom: 8 }}>{FARMER.role}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                  <ContactRow icon={<Mail size={13} color="var(--agri-text-muted)" />} text={form.email} />
                  <ContactRow icon={<Phone size={13} color="var(--agri-text-muted)" />} text={form.phone} />
                  <ContactRow icon={<MapPin size={13} color="var(--agri-text-muted)" />} text={form.location} />
                </div>
              </div>
            </div>

            {editing ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, borderTop: '1px solid var(--agri-border)', paddingTop: 16 }}>
                {['name','email','phone','location'].map(k => (
                  <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <label style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: 'var(--agri-text)', textTransform: 'capitalize' }}>
                      {k === 'location' ? 'Location' : k.charAt(0).toUpperCase() + k.slice(1)}
                    </label>
                    <input value={form[k]} onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}
                      style={{ padding: '8px 10px', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', outline: 'none', background: 'white' }} />
                  </div>
                ))}
                <div style={{ display: 'flex', gap: 10 }}>
                  <button onClick={() => setEditing(false)} style={{ padding: '8px 16px', border: '1px solid var(--agri-border)', borderRadius: 6, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, cursor: 'pointer' }}>Cancel</button>
                  <GreenBtn onClick={() => setEditing(false)}>Save Changes</GreenBtn>
                </div>
              </div>
            ) : (
              <GreenBtn onClick={() => setEditing(true)}>Edit Profile</GreenBtn>
            )}
          </div>
        </div>

        {/* Right: Account Actions */}
        <div style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden', alignSelf: 'start' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--agri-border)' }}>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)' }}>Account Actions</span>
          </div>
          <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <button style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', border: '1px solid var(--agri-border)', borderRadius: 6, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', cursor: 'pointer', textAlign: 'left', width: '100%' }}>
              <Lock size={15} color="var(--agri-text-secondary)" />
              Change Password
            </button>
            <button onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', border: '1px solid var(--agri-error-bg)', borderRadius: 6, background: '#FEF2F2', fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-error)', cursor: 'pointer', textAlign: 'left', width: '100%' }}>
              <LogOut size={15} color="var(--agri-error)" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function ContactRow({ icon, text }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
      {icon}
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)' }}>{text}</span>
    </div>
  )
}
