import logoImg from '../imports/image-5.png'

export function AgriLogo({ size = 42, badgeBg = 'white' }) {
  const inner = Math.round(size * 0.86)
  return (
    <div style={{
      width: size, height: size,
      borderRadius: Math.round(size * 0.24),
      background: badgeBg,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0, overflow: 'hidden',
    }}>
      <img src={logoImg} alt="AgriConnect" style={{ width: inner, height: inner, objectFit: 'contain' }} />
    </div>
  )
}
