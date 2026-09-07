import { useState } from 'react'
import { CheckCircle, Loader2 } from 'lucide-react'
import { GreenBtn } from './Dashboard'

const NOTIFICATION_PREFS = [
  { key: 'orders',       label: 'Order updates' },
  { key: 'verification', label: 'Verification updates' },
  { key: 'shipments',    label: 'Shipment updates' },
  { key: 'marketing',    label: 'Marketing and tips' },
]

const LANGUAGES  = ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Marathi']
const TIMEZONES  = ['(GMT+5:30) India Standard Time', '(GMT+0:00) UTC', '(GMT-5:00) Eastern Time']

export default function Settings() {
  const [notifs, setNotifs] = useState({ orders: true, verification: true, shipments: true, marketing: true })
  const [lang,   setLang]   = useState('English')
  const [tz,     setTz]     = useState('(GMT+5:30) India Standard Time')
  const [saveState, setSaveState] = useState(null)

  function save() {
    setSaveState('loading')
    setTimeout(() => { setSaveState('success'); setTimeout(() => setSaveState(null), 1200) }, 700)
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Settings</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>Manage your preferences</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, alignItems: 'start' }}>
        {/* Notification Preferences */}
        <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--agri-border)' }}>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)' }}>Notification Preferences</span>
          </div>
          <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {NOTIFICATION_PREFS.map(n => (
              <label key={n.key} style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                {/* using <input type="checkbox"> instead of <Checkbox>: Checkbox kit component requires label/description
                    props and renders its own layout; here we need a checkbox inline in a custom label row */}
                <input type="checkbox" checked={notifs[n.key]} onChange={e => setNotifs(p => ({ ...p, [n.key]: e.target.checked }))}
                  style={{ width: 16, height: 16, accentColor: 'var(--agri-primary)', cursor: 'pointer', flexShrink: 0 }} />
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)' }}>{n.label}</span>
              </label>
            ))}
          </div>
        </section>

        {/* Display Preferences */}
        <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--agri-border)' }}>
            <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: 'var(--agri-text)' }}>Display Preferences</span>
          </div>
          <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              <label style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: 'var(--agri-text)' }}>Language</label>
              {/* using <select> instead of <SelectField>: simple settings dropdown */}
              <select value={lang} onChange={e => setLang(e.target.value)}
                style={{ padding: '8px 10px', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', background: 'white', outline: 'none', cursor: 'pointer' }}>
                {LANGUAGES.map(l => <option key={l}>{l}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              <label style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: 'var(--agri-text)' }}>Timezone</label>
              <select value={tz} onChange={e => setTz(e.target.value)}
                style={{ padding: '8px 10px', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', background: 'white', outline: 'none', cursor: 'pointer' }}>
                {TIMEZONES.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>
        </section>
      </div>

      {/* Save */}
      <div>
        <button onClick={save} disabled={saveState === 'loading'}
          style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '9px 20px', background: 'var(--agri-primary)', color: 'white', border: 'none', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, cursor: 'pointer' }}>
          {saveState === 'loading'
            ? <><Loader2 size={14} className="animate-spin" /> Saving…</>
            : saveState === 'success'
            ? <><CheckCircle size={14} /> Saved!</>
            : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}
