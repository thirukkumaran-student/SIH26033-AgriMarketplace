import { CheckCircle, Upload } from 'lucide-react'
import { DOCUMENTS, DOC_STATUS_VARIANT, FARMER } from '../data'
import { Th, Td, GreenBtn, StatusPill } from './Dashboard'

const GRID = '1.5fr 1.5fr 1fr 0.8fr 80px'
const COLS = ['Document Type', 'Document Number', 'Submitted On', 'Status', 'Action']

export default function Verification() {
  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Verification</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>Submit documents and track your verification status</p>
      </div>

      {/* Status banner */}
      <div style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 52, height: 52, borderRadius: 12, background: '#DCFCE7', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <CheckCircle size={26} color="var(--agri-success)" />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: 'var(--agri-text-secondary)', marginBottom: 2 }}>Verification Status</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-success)', lineHeight: 1.2 }}>Verified</div>
            <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)', marginTop: 3 }}>
              Your documents have been approved. You can now list your produce.
            </div>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-muted)' }}>Verified On</div>
          <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'var(--agri-text)' }}>{FARMER.verifiedOn}</div>
        </div>
      </div>

      {/* Documents table */}
      <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid var(--agri-border)' }}>
          <h2 style={{ fontFamily: 'var(--agri-font)', fontSize: 18, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Submitted Documents</h2>
          <GreenBtn onClick={() => {}}><Upload size={14} strokeWidth={2} /> Upload Document</GreenBtn>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: GRID, padding: '12px 20px', background: '#F8FAFB', borderBottom: '1px solid var(--agri-border)' }}>
          {COLS.map(c => <Th key={c}>{c}</Th>)}
        </div>

        {DOCUMENTS.map((doc, i) => (
          <div key={doc.type} style={{ display: 'grid', gridTemplateColumns: GRID, padding: '13px 20px', alignItems: 'center', borderBottom: i < DOCUMENTS.length - 1 ? '1px solid var(--agri-border-light)' : 'none' }}>
            <Td bold>{doc.type}</Td>
            <Td muted>{doc.number}</Td>
            <Td muted>{doc.submittedOn}</Td>
            <StatusPill status={doc.status} variant={DOC_STATUS_VARIANT[doc.status]} />
            <button style={{ padding: '6px 14px', background: 'white', border: '1px solid var(--agri-border)', borderRadius: 8, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-primary)', cursor: 'pointer' }}>
              View
            </button>
          </div>
        ))}
      </section>
    </div>
  )
}
