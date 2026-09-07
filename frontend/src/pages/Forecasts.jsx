import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const FORECAST_DATA = [
  { crop: 'Tomato',  currentPrice: 40,  forecastPrice: 48,  trend: 'up',   confidence: 82, reason: 'Seasonal demand increase expected in Oct–Nov.' },
  { crop: 'Rice',    currentPrice: 55,  forecastPrice: 53,  trend: 'down', confidence: 70, reason: 'New harvest season will increase supply.' },
  { crop: 'Mango',   currentPrice: 90,  forecastPrice: 90,  trend: 'flat', confidence: 60, reason: 'Off-season; price likely to remain stable.' },
  { crop: 'Wheat',   currentPrice: 30,  forecastPrice: 34,  trend: 'up',   confidence: 75, reason: 'Export demand expected to rise.' },
  { crop: 'Onion',   currentPrice: 25,  forecastPrice: 18,  trend: 'down', confidence: 68, reason: 'Bumper crop in Maharashtra may depress prices.' },
]

const TREND_COLOR = { up: 'var(--agri-success)', down: 'var(--agri-error)', flat: 'var(--agri-warning)' }
const TREND_ICON  = { up: TrendingUp, down: TrendingDown, flat: Minus }

export default function Forecasts() {
  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h1 style={{ fontFamily: 'var(--agri-font)', fontSize: 24, fontWeight: 700, color: 'var(--agri-text)', margin: 0 }}>Forecasts</h1>
        <p style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)', margin: '4px 0 0' }}>Market price forecasts for the next 30 days</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {FORECAST_DATA.map(row => {
          const Icon  = TREND_ICON[row.trend]
          const color = TREND_COLOR[row.trend]
          const delta = row.forecastPrice - row.currentPrice
          return (
            <div key={row.crop} style={{ background: 'white', border: '1px solid var(--agri-border)', borderRadius: 'var(--agri-radius-lg)', padding: 16, display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ width: 44, height: 44, borderRadius: 'var(--agri-radius-md)', background: color+'18', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon size={20} color={color}/>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 2 }}>
                  <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color: 'var(--agri-text)' }}>{row.crop}</span>
                  <span style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)' }}>
                    ₹{row.currentPrice}/kg → <strong style={{ color }}>₹{row.forecastPrice}/kg</strong>
                    {delta !== 0 && <span style={{ color, marginLeft: 4 }}>({delta > 0 ? '+' : ''}{delta})</span>}
                  </span>
                </div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-secondary)' }}>{row.reason}</div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 15, color: 'var(--agri-text-muted)', marginBottom: 2 }}>Confidence</div>
                <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, fontWeight: 600, color }}>{row.confidence}%</div>
              </div>
            </div>
          )
        })}
      </div>

      <div style={{ fontFamily: 'var(--agri-font)', fontSize: 14, color: 'var(--agri-text-muted)', textAlign: 'center' }}>
        Forecasts are indicative only and based on regional market trends. Updated weekly.
      </div>
    </div>
  )
}
