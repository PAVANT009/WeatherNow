/** Format an ISO datetime in the user's local timezone. */
export function formatLocalDateTime(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) {
    return iso
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function formatTemperature(value: string | number): string {
  const num = typeof value === 'number' ? value : Number(value)
  if (Number.isNaN(num)) {
    return `${value} °C`
  }
  return `${num.toFixed(1)} °C`
}

export function formatHumidity(value: number | string): string {
  return `${value} %`
}

export function formatWind(value: string | number): string {
  const num = typeof value === 'number' ? value : Number(value)
  if (Number.isNaN(num)) {
    return `${value} km/h`
  }
  return `${num.toFixed(1)} km/h`
}
