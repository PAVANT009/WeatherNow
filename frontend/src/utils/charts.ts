export function metricUnit(metric: 'temperature' | 'humidity' | 'wind_speed'): string {
  if (metric === 'temperature') return '°C'
  if (metric === 'humidity') return '%'
  return 'km/h'
}

export function metricLabel(metric: 'temperature' | 'humidity' | 'wind_speed'): string {
  if (metric === 'temperature') return 'Sıcaklık'
  if (metric === 'humidity') return 'Nem'
  return 'Rüzgâr'
}

/** Parse "12, 18, 21" or "[12,18,21]" into numbers. */
export function parseNumberList(raw: string): number[] {
  const cleaned = raw.trim().replace(/^\[/, '').replace(/\]$/, '')
  if (!cleaned) {
    return []
  }
  return cleaned.split(/[\s,;]+/).filter(Boolean).map((part) => {
    const value = Number(part)
    if (Number.isNaN(value)) {
      throw new Error(`Geçersiz sayı: ${part}`)
    }
    return value
  })
}

export function toNumber(value: string | number): number {
  return typeof value === 'number' ? value : Number(value)
}
