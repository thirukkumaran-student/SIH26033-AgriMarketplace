import { useState } from 'react'
import { useNavigate } from 'react-router'
import { ChevronRight, FileText, Check, X } from 'lucide-react'
import { FARMER_DETAIL } from '../data/adminData'

const STEPS = ['Submitted', 'Under Review', 'Approved']

export default function FarmerVerificationDetail() {
  const navigate = useNavigate()
  const f = FARMER_DETAIL
  const [status, setStatus] = useState('Under Review')
  const [reason, setReason] = useState('')
  const [showReject, setShowReject] = useState(false)

  const stepIndex = { Submitted: 0, 'Under Review': 1, Approved: 2, Rejected: -1 }[status] ?? 1

  function approve() { setStatus('Approved'); setShowReject(false) }
  function reject() {
    if (!showReject) { setShowReject(true); return }
    if (reason.trim()) setStatus('Rejected')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280' }}>
        <button onClick={() => navigate('/admin/verification')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--agri-font)', fontSize: 14, color: '#166534', fontWeight: 600, padding: 0 }}>Farmer Verification</button>
        <ChevronRight size={14} />
        <span style={{ color: '#374151', fontWeight: 600 }}>{f.name}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

          {/* Farmer Info */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 18 }}>Farmer Information</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
              <div style={{ width: 56, height: 56, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--agri-font)', fontSize: 20, fontWeight: 800, color: '#166534' }}>{f.avatar}</div>
              <div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 19, fontWeight: 700, color: '#111827' }}>{f.name}</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>{f.id}</div>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              {[
                ['Phone', f.phone], ['Email', f.email],
                ['Location', f.location], ['Farm Size', f.farmSize],
                ['Primary Crops', f.primaryCrops], ['Submitted', f.submittedAt],
              ].map(([label, val]) => (
                <div key={label}>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 12, color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>{label}</div>
                  <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: '#374151' }}>{val}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Documents */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 16 }}>Uploaded Documents</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {f.documents.map((doc, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '13px 16px', border: '1.5px solid #e5e7eb', borderRadius: 10 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#166534' }}>
                    <FileText size={18} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#111827' }}>{doc.name}</div>
                    <div style={{ fontFamily: 'var(--agri-font)', fontSize: 13, color: '#9ca3af' }}>{doc.file}</div>
                  </div>
                  <button style={{ padding: '6px 14px', borderRadius: 8, border: '1.5px solid #e5e7eb', background: 'white', fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: '#374151', cursor: 'pointer' }}>View</button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

          {/* Verification Status Stepper */}
          <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 20 }}>Verification Status</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {status === 'Rejected'
                ? (
                  <>
                    {STEPS.slice(0,2).map((step, i) => (
                      <StepItem key={step} label={step} state="done" isLast={false} />
                    ))}
                    <StepItem label="Rejected" state="rejected" isLast={true} />
                  </>
                )
                : STEPS.map((step, i) => (
                  <StepItem key={step} label={step}
                    state={i < stepIndex ? 'done' : i === stepIndex ? 'active' : 'pending'}
                    isLast={i === STEPS.length - 1} />
                ))
              }
            </div>
          </div>

          {/* Actions */}
          {status === 'Pending' || status === 'Under Review' ? (
            <div style={{ background: 'white', borderRadius: 14, border: '1px solid #e7f0eb', padding: '22px 24px' }}>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 16 }}>Actions</div>
              {showReject && (
                <textarea value={reason} onChange={e => setReason(e.target.value)} placeholder="Rejection reason..." rows={3}
                  style={{ width: '100%', marginBottom: 12, padding: '10px 12px', border: '1.5px solid #e5e7eb', borderRadius: 9, fontFamily: 'var(--agri-font)', fontSize: 14, color: '#374151', resize: 'vertical', outline: 'none', boxSizing: 'border-box' }} />
              )}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <button onClick={approve} style={{ width: '100%', padding: '12px', background: '#166534', border: 'none', borderRadius: 9, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 700, color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <Check size={16} /> Approve Farmer
                </button>
                <button onClick={reject} style={{ width: '100%', padding: '12px', background: 'white', border: '1.5px solid #dc2626', borderRadius: 9, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 600, color: '#dc2626', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <X size={16} /> {showReject ? 'Confirm Rejection' : 'Reject Farmer'}
                </button>
              </div>
            </div>
          ) : (
            <div style={{ background: status === 'Approved' ? '#f0fdf4' : '#fef2f2', borderRadius: 14, border: `1px solid ${status === 'Approved' ? '#bbf7d0' : '#fecaca'}`, padding: '22px 24px', textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 32, marginBottom: 8 }}>{status === 'Approved' ? '✓' : '✗'}</div>
              <div style={{ fontFamily: 'var(--agri-font)', fontSize: 16, fontWeight: 700, color: status === 'Approved' ? '#166534' : '#dc2626' }}>Farmer {status}</div>
              {reason && <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: '#6b7280', marginTop: 8 }}>{reason}</div>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StepItem({ label, state, isLast }) {
  const colors = { done: { dot: '#166534', line: '#bbf7d0', text: '#166534' }, active: { dot: '#166534', line: '#e5e7eb', text: '#111827' }, pending: { dot: '#e5e7eb', line: '#e5e7eb', text: '#9ca3af' }, rejected: { dot: '#dc2626', line: '#fecaca', text: '#dc2626' } }
  const c = colors[state] || colors.pending
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ width: 22, height: 22, borderRadius: '50%', background: c.dot, border: `3px solid ${state === 'active' ? '#166534' : c.dot}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {state === 'done' && <Check size={11} color="white" strokeWidth={3} />}
        </div>
        {!isLast && <div style={{ width: 2, height: 28, background: c.line, marginTop: 2 }} />}
      </div>
      <div style={{ paddingTop: 1, paddingBottom: isLast ? 0 : 16 }}>
        <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: state === 'active' ? 700 : 500, color: c.text }}>{label}</div>
      </div>
    </div>
  )
}
