/** Chart colors and helpers for the compare page. */

export const SERIES_COLORS = [
  '#0061a5',
  '#0e8a6c',
  '#c47b16',
  '#7c3aed',
  '#dc2626',
] as const

export function chartColor(index: number): string {
  return SERIES_COLORS[index % SERIES_COLORS.length]
}

export function readCssVar(name: string, fallback: string): string {
  if (typeof window === 'undefined') {
    return fallback
  }
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim()
  return value || fallback
}
