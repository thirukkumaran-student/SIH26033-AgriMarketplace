import { useState } from 'react'
import { Search, Plus, Pencil, Trash2, CheckCircle, AlertCircle, Loader2, UploadCloud, X } from 'lucide-react'
import {
  PRODUCE_LIST, PRODUCE_IMAGES, DEFAULT_IMG,
  PRODUCE_STATUS_VARIANT, CROP_CATEGORIES, STATUS_OPTIONS,
} from '../data'
import { Th, Td, GreenBtn, ProduceThumb, StatusPill } from './Dashboard'

const GRID   = '1.8fr 1fr 1fr 1fr 1fr 1fr 100px'
const COLS   = ['Product','Category','Quantity','Price/Unit','Status','Updated','Actions']
const PER_PAGE = 6

export default function MyProduce() {
  const [items, setItems]     = useState(PRODUCE_LIST.map(p => ({ ...p })))
  const [search, setSearch]   = useState('')
  const [cat, setCat]         = useState('All Categories')
  const [status, setStatus]   = useState('All Status')
  const [page, setPage]       = useState(1)
  const [modal, setModal]     = useState(null)   // null | { mode:'add'|'edit'|'delete', item? }
  const [formState, setFormState] = useState(null)
  const [form, setForm]       = useState({})

  const filtered = items.filter(p => {
    const q = search.toLowerCase()
    return (
      p.name.toLowerCase().includes(q) &&
      (cat    === 'All Categories' || p.category === cat) &&
      (status === 'All Status'     || p.status   === status)
    )
  })
  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE))
  const pageItems  = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE)

  function openAdd() {
    setForm({ name: '', category: 'Vegetables', qty: '', unit: 'kg', price: '', status: 'Available', description: '' })
    setFormState(null); setModal({ mode: 'add' })
  }
  function openEdit(item) {
    setForm({ ...item, qty: String(item.qty), price: String(item.price) })
    setFormState(null); setModal({ mode: 'edit', item })
  }
  function openDelete(item) {
    setFormState(null); setModal({ mode: 'delete', item })
  }
  function closeModal() { setModal(null); setFormState(null) }

  function handleSave() {
    if (!form.name || !form.qty || !form.price) { setFormState('error'); return }
    setFormState('loading')
    setTimeout(() => {
      const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, ' ')
      if (modal.mode === 'add') {
        setItems(prev => [...prev, { ...form, id: Date.now(), qty: Number(form.qty), price: Number(form.price), updated: today }])
      } else {
        setItems(prev => prev.map(p => p.id === modal.item.id ? { ...p, ...form, qty: Number(form.qty), price: Number(form.price), updated: today } : p))
      }
      setFormState('success')
      setTimeout(closeModal, 900)
    }, 800)
  }

  function handleDelete() {
    setItems(prev => prev.filter(p => p.id !== modal.item.id))
    closeModal()
  }

  const isAdd = modal?.mode === 'add', isEdit = modal?.mode === 'edit', isDel = modal?.mode === 'delete'
  const saving = formState === 'loading', success = formState === 'success', hasErr = formState === 'error'

  return (
    <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Title */}
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>My Produce</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>Manage your produce listings and availability</p>
      </div>

      {/* Filters row */}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Search produce..." />
        <FilterSelect value={status} onChange={v => { setStatus(v); setPage(1) }} options={STATUS_OPTIONS} />
        <FilterSelect value={cat}    onChange={v => { setCat(v);    setPage(1) }} options={CROP_CATEGORIES} />
        <GreenBtn onClick={openAdd}><Plus size={15} strokeWidth={2.5} /> Add Produce</GreenBtn>
      </div>

      {/* Table */}
      <section style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: GRID, padding: '12px 20px', background: '#F8FAFB', borderBottom: '1px solid var(--agri-border)' }}>
          {COLS.map(c => <Th key={c}>{c}</Th>)}
        </div>

        {pageItems.length === 0
          ? <Empty text="No produce found" />
          : pageItems.map((row, i) => (
            <div key={row.id} style={{ display: 'grid', gridTemplateColumns: GRID, padding: '10px 20px', alignItems: 'center', borderBottom: i < pageItems.length - 1 ? '1px solid var(--agri-border-light)' : 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <ProduceThumb name={row.name} />
                <Td bold>{row.name}</Td>
              </div>
              <Td muted>{row.category}</Td>
              <Td>{row.qty} {row.unit}</Td>
              <Td>₹{row.price}/{row.unit}</Td>
              <StatusPill status={row.status} variant={PRODUCE_STATUS_VARIANT[row.status]} />
              <Td muted>{row.updated}</Td>
              <div style={{ display: 'flex', gap: 6 }}>
                <IconBtn onClick={() => openEdit(row)} title="Edit"   color="var(--agri-text-secondary)"><Pencil size={15} /></IconBtn>
                <IconBtn onClick={() => openDelete(row)} title="Delete" color="var(--agri-error)"><Trash2 size={15} /></IconBtn>
              </div>
            </div>
          ))
        }

        {/* Pagination */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 20px', borderTop: '1px solid var(--agri-border)' }}>
          <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)' }}>
            Showing {Math.min((page - 1) * PER_PAGE + 1, filtered.length)}–{Math.min(page * PER_PAGE, filtered.length)} of {filtered.length} items
          </span>
          <Pagination page={page} total={totalPages} onChange={setPage} />
        </div>
      </section>

      {/* Add/Edit Modal */}
      {(isAdd || isEdit) && (
        <AgriModal onClose={closeModal} title={isAdd ? 'Add New Produce' : 'Edit Produce'}
          subtitle={isAdd ? 'List your farm produce and reach more buyers' : 'Update your produce details'}
          footer={success ? null : (
            <ModalFooter>
              <ModalBtn outline onClick={closeModal} disabled={saving}>Cancel</ModalBtn>
              <ModalBtn primary onClick={handleSave} disabled={saving}>
                {saving ? <><Loader2 size={14} className="animate-spin" style={{ display: 'inline' }} /> Saving…</> : isAdd ? 'Add Produce' : 'Save Changes'}
              </ModalBtn>
            </ModalFooter>
          )}>
          {success
            ? <SuccessBanner text={isAdd ? 'Produce added!' : 'Produce updated!'} />
            : <AddEditForm form={form} setForm={setForm} hasErr={hasErr} isEdit={isEdit} />}
        </AgriModal>
      )}

      {/* Delete Modal */}
      {isDel && (
        <AgriModal onClose={closeModal} title="Delete Produce" size="small"
          footer={
            <ModalFooter>
              <ModalBtn outline onClick={closeModal}>Cancel</ModalBtn>
              <ModalBtn danger onClick={handleDelete}>Delete</ModalBtn>
            </ModalFooter>
          }>
          <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: 0 }}>
            Are you sure you want to delete <strong style={{ color: 'var(--agri-text)' }}>{modal.item?.name}</strong>? This cannot be undone.
          </p>
        </AgriModal>
      )}
    </div>
  )
}

/* ── Add/Edit Form ── */
function AddEditForm({ form, setForm, hasErr, isEdit }) {
  const f = k => e => setForm(p => ({ ...p, [k]: e.target.value }))
  const descLen = (form.description || '').length
  const imgSrc = form.name && PRODUCE_IMAGES[form.name] ? PRODUCE_IMAGES[form.name] : null

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {hasErr && <ErrBanner />}

      <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr', gap: 20, alignItems: 'start' }}>
        {/* Left: image upload / preview */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
          {isEdit && imgSrc ? (
            <>
              <div style={{ width: '100%', aspectRatio: '4/3', borderRadius: 8, overflow: 'hidden', border: '1px solid var(--agri-border)' }}>
                <img src={imgSrc} alt={form.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <button style={{ width: '100%', padding: '7px 0', border: '1px solid var(--agri-primary)', borderRadius: 6, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: 'var(--agri-primary)', cursor: 'pointer' }}>
                Change Image
              </button>
              <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)', textAlign: 'center', margin: 0, lineHeight: 1.6 }}>
                PNG, JPG, WebP, GIF, HEIC<br />Max 5MB
              </p>
            </>
          ) : (
            <>
              <div style={{ width: '100%', aspectRatio: '4/3', borderRadius: 8, border: '1.5px dashed var(--agri-border)', background: '#f9fafb', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 12 }}>
                <UploadCloud size={32} color="var(--agri-text-muted)" strokeWidth={1.5} />
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'var(--agri-text)', textAlign: 'center' }}>Upload Product Image</span>
                <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)', textAlign: 'center', lineHeight: 1.6 }}>PNG, JPG, WebP, GIF, HEIC<br />Max 5MB</span>
              </div>
              <button style={{ width: '100%', padding: '7px 0', border: '1px solid var(--agri-primary)', borderRadius: 6, background: 'white', fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, color: 'var(--agri-primary)', cursor: 'pointer' }}>
                Choose Image
              </button>
              <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)', textAlign: 'center', margin: 0, lineHeight: 1.6 }}>
                A clear image helps buyers<br />identify your produce.
              </p>
            </>
          )}
        </div>

        {/* Right: form fields */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Field label="Product Name *">
            <FInput value={form.name} onChange={f('name')} placeholder="e.g. Tomato" />
          </Field>
          <Field label="Category *">
            <FSelect value={form.category} onChange={f('category')} options={['Vegetables','Grains','Fruits','Other']} />
          </Field>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Field label="Quantity *">
              <FInput value={form.qty} onChange={f('qty')} placeholder="100" type="number" />
            </Field>
            <Field label="Unit *">
              <FSelect value={form.unit} onChange={f('unit')} options={['kg','quintal','ton','pieces']} />
            </Field>
          </div>
          <Field label="Price per Unit (₹) *">
            <FInput value={form.price} onChange={f('price')} placeholder="e.g. 40" type="number" />
          </Field>
          <Field label="Status *">
            <FSelect value={form.status} onChange={f('status')} options={['Available','Low Stock','Out of Stock']} />
          </Field>
        </div>
      </div>

      {/* Description — full width */}
      <Field label="Description">
        <textarea
          value={form.description}
          onChange={f('description')}
          placeholder="Fresh and organic produce grown with natural methods."
          rows={3}
          maxLength={500}
          style={{ ...inputBase, resize: 'vertical', fontFamily: 'var(--agri-font)' }}
        />
        <div style={{ textAlign: 'right', fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)', marginTop: 3 }}>
          {descLen}/500
        </div>
      </Field>
    </div>
  )
}

const inputBase = { width: '100%', padding: '9px 12px', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', background: '#ffffff', outline: 'none', boxSizing: 'border-box' }

function Field({ label, children }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
      <label style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 500, color: 'var(--agri-text)' }}>{label}</label>
      {children}
    </div>
  )
}
function FInput({ value, onChange, placeholder, type = 'text' }) {
  return <input type={type} value={value} onChange={onChange} placeholder={placeholder} style={inputBase} />
}
function FSelect({ value, onChange, options }) {
  return (
    <select value={value} onChange={onChange} style={{ ...inputBase, cursor: 'pointer', appearance: 'auto' }}>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  )
}

/* ── Custom AgriConnect Modal (replaces kit Modal — avoids dark-mode theming conflict) ── */
function AgriModal({ title, subtitle, children, footer, onClose, size = 'large' }) {
  const widths = { small: 420, large: 680 }
  return (
    <div
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ background: '#ffffff', borderRadius: 12, width: '100%', maxWidth: widths[size] || widths.large, maxHeight: '90vh', display: 'flex', flexDirection: 'column', boxShadow: '0 20px 60px rgba(0,0,0,0.15)' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', padding: '20px 24px 0' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--agri-font)', fontSize: 18, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>{title}</h2>
            {subtitle && <p style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>{subtitle}</p>}
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--agri-text-muted)', display: 'flex', alignItems: 'center', flexShrink: 0, marginLeft: 16 }}>
            <X size={18} />
          </button>
        </div>
        {/* Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {children}
        </div>
        {/* Footer */}
        {footer && (
          <div style={{ padding: '0 24px 20px' }}>
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
function ModalFooter({ children }) {
  return <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', paddingTop: 16, borderTop: '1px solid var(--agri-border)' }}>{children}</div>
}
function ModalBtn({ children, onClick, disabled, outline, primary, danger }) {
  const bg = danger ? 'var(--agri-error)' : primary ? 'var(--agri-primary)' : 'white'
  const color = (primary || danger) ? '#ffffff' : 'var(--agri-text)'
  const border = outline ? '1px solid var(--agri-border)' : 'none'
  return (
    <button onClick={onClick} disabled={disabled} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '9px 20px', background: bg, color, border, borderRadius: 8, fontFamily: 'var(--agri-font)', fontSize: 15, fontWeight: 500, cursor: disabled ? 'default' : 'pointer', opacity: disabled ? 0.6 : 1 }}>
      {children}
    </button>
  )
}

/* ── Shared small components ── */
export { Td } from './Dashboard'
export function SearchInput({ value, onChange, placeholder }) {
  return (
    <div style={{ position: 'relative', flex: 1, maxWidth: 260 }}>
      <Search size={14} color="var(--agri-text-muted)" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
      <input value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
        style={{ width: '100%', padding: '8px 10px 8px 30px', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', background: 'white', outline: 'none', boxSizing: 'border-box' }} />
    </div>
  )
}
export function FilterSelect({ value, onChange, options }) {
  return (
    /* using <select> instead of <SelectField>: simple inline filter; no need for kit-managed state */
    <select value={value} onChange={e => onChange(e.target.value)}
      style={{ padding: '7px 10px', border: '1px solid var(--agri-border)', borderRadius: 6, fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text)', background: 'white', cursor: 'pointer', outline: 'none' }}>
      {options.map(o => <option key={o}>{o}</option>)}
    </select>
  )
}
export function Pagination({ page, total, onChange }) {
  if (total <= 1) return null
  const pages = Array.from({ length: total }, (_, i) => i + 1)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <PagBtn onClick={() => onChange(Math.max(1, page - 1))} disabled={page === 1}>‹</PagBtn>
      {pages.map(p => (
        <PagBtn key={p} active={p === page} onClick={() => onChange(p)}>{p}</PagBtn>
      ))}
      <PagBtn onClick={() => onChange(Math.min(total, page + 1))} disabled={page === total}>›</PagBtn>
    </div>
  )
}
function PagBtn({ children, active, disabled, onClick }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{ minWidth: 28, height: 28, padding: '0 6px', border: `1px solid ${active ? 'var(--agri-primary)' : 'var(--agri-border)'}`, borderRadius: 4, background: active ? 'var(--agri-primary)' : 'white', color: active ? 'white' : disabled ? 'var(--agri-text-muted)' : 'var(--agri-text)', fontFamily: 'var(--agri-font)', fontSize: 15, cursor: disabled ? 'default' : 'pointer' }}>
      {children}
    </button>
  )
}
export function Empty({ text }) {
  return <div style={{ padding: '32px 16px', textAlign: 'center', fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)' }}>{text}</div>
}
function IconBtn({ children, onClick, title, color }) {
  return (
    <button onClick={onClick} title={title} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color, display: 'flex', alignItems: 'center' }}>
      {children}
    </button>
  )
}
function SuccessBanner({ text }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 14px', background: '#DCFCE7', borderRadius: 6 }}>
      <CheckCircle size={16} color="var(--agri-success)" />
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-success)' }}>{text}</span>
    </div>
  )
}
function ErrBanner() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px', background: '#FEE2E2', borderRadius: 6 }}>
      <AlertCircle size={15} color="var(--agri-error)" />
      <span style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-error)' }}>Please fill in all required fields.</span>
    </div>
  )
}
