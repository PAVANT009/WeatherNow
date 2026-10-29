export function metricUnit(metric: 'temperature' | 'humidity' | 'wind_speed'): string {
  if (metric === 'temperature') return '°C'
  if (metric === 'humidity') return '%'
  return 'km/h'
}

export function metricLabel(metric: 'temperature' | 'humidity' | 'wind_speed'): string {
  if (metric === 'temperature') return 'Temperature'
  if (metric === 'humidity') return 'Humidity'
  return 'Wind speed'
}

export function parseNumberList(raw: string): number[] {
  const cleaned = raw.trim().replace(/^\[/, '').replace(/\]$/, '')
  if (!cleaned) return []
  return cleaned.split(/[\s,;]+/).filter(Boolean).map((part) => {
    const value = Number(part)
    if (Number.isNaN(value)) throw new Error(`Invalid number: ${part}`)
    return value
  })
}

export function toNumber(value: string | number): number { return typeof value === 'number' ? value : Number(value) }
