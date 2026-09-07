import { useState } from 'react'
import { Check, Shield, Bell, DollarSign, Sliders } from 'lucide-react'

export default function AdminSettings() {
  const [commission, setCommission] = useState('2.5')
  const [disputeTimeout, setDisputeTimeout] = useState('48')
  const [autoVerify, setAutoVerify] = useState(true)
  const [notifications, setNotifications] = useState(true)
  const [saved, setSaved] = useState(false)

  function handleSave(e) {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, fontFamily: 'var(--agri-font)', maxWidth: 800 }}>
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>Admin Settings</h1>
        <p style={{ fontSize: 15, color: '#6b7280', margin: '4px 0 0' }}>Configure platform marketplace rules, verification policies, and notifications</p>
      </div>

      {saved && (
        <div style={{ background: '#dcfce7', border: '1px solid #bbf7d0', borderRadius: 8, padding: '12px 16px', color: '#166534', fontSize: 14, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Check size={16} /> Settings saved successfully!
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Marketplace Fees */}
        <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 14, padding: 22 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <DollarSign size={20} color="#166534" />
            <h2 style={{ fontSize: 17, fontWeight: 700, color: '#111827', margin: 0 }}>Marketplace Fees & Payouts</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: 14, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 6 }}>
                Platform Commission (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={commission}
                onChange={e => setCommission(e.target.value)}
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 14, outline: 'none' }}
              />
              <span style={{ fontSize: 12, color: '#9ca3af', marginTop: 4, display: 'block' }}>Charged on successful completed orders</span>
            </div>

            <div>
              <label style={{ fontSize: 14, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 6 }}>
                Dispute Timeout (Hours)
              </label>
              <input
                type="number"
                value={disputeTimeout}
                onChange={e => setDisputeTimeout(e.target.value)}
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 14, outline: 'none' }}
              />
              <span style={{ fontSize: 12, color: '#9ca3af', marginTop: 4, display: 'block' }}>Window before auto-escalation to admin review</span>
            </div>
          </div>
        </div>

        {/* Verification & Security */}
        <div style={{ background: 'white', border: '1px solid #e7f0eb', borderRadius: 14, padding: 22 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <Shield size={20} color="#166534" />
            <h2 style={{ fontSize: 17, fontWeight: 700, color: '#111827', margin: 0 }}>Verification Policies</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 600, color: '#111827' }}>Mandatory Land Record Document</div>
                <div style={{ fontSize: 13, color: '#6b7280' }}>Require patta/chitta document for farmer verification</div>
              </div>
              <input type="checkbox" checked={autoVerify} onChange={e => setAutoVerify(e.target.checked)} style={{ width: 18, height: 18, accentColor: '#166534' }} />
            </label>

            <div style={{ height: 1, background: '#f3f4f6' }} />

            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 600, color: '#111827' }}>Automated SMS & WhatsApp Alerts</div>
                <div style={{ fontSize: 13, color: '#6b7280' }}>Notify farmers and consumers on status transitions</div>
              </div>
              <input type="checkbox" checked={notifications} onChange={e => setNotifications(e.target.checked)} style={{ width: 18, height: 18, accentColor: '#166534' }} />
            </label>
          </div>
        </div>

        <button
          type="submit"
          style={{
            alignSelf: 'flex-start',
            padding: '11px 28px',
            background: '#166534',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            fontSize: 15,
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Save Platform Settings
        </button>
      </form>
    </div>
  )
}
