import React from 'react'

export function Avatar({
  type = 'image',
  src,
  size = 'medium',
  shape = 'circle',
  initials = 'AC',
  alt = 'Avatar',
  style = {},
}) {
  const sizeMap = {
    small: { width: 32, height: 32, fontSize: 12 },
    medium: { width: 40, height: 40, fontSize: 14 },
    large: { width: 48, height: 48, fontSize: 16 },
    xlarge: { width: 64, height: 64, fontSize: 20 },
  }

  const dims = sizeMap[size] || sizeMap.medium
  const borderRadius = shape === 'circle' ? '50%' : '8px'

  if (src && type === 'image') {
    return (
      <img
        src={src}
        alt={alt}
        style={{
          width: dims.width,
          height: dims.height,
          borderRadius,
          objectFit: 'cover',
          display: 'block',
          flexShrink: 0,
          ...style,
        }}
      />
    )
  }

  return (
    <div
      style={{
        width: dims.width,
        height: dims.height,
        borderRadius,
        background: '#dcfce7',
        color: '#166534',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 700,
        fontSize: dims.fontSize,
        flexShrink: 0,
        ...style,
      }}
    >
      {initials}
    </div>
  )
}

export default Avatar
