import { metricLabel, metricUnit } from '../utils'
import type { WeatherMetric } from '../types'
import styles from './CompareTooltip.module.css'

type PayloadItem = {
  name?: string
  value?: number | string
  color?: string
  dataKey?: string | number
}

interface CompareTooltipProps {
  metric: WeatherMetric
  active?: boolean
  payload?: PayloadItem[]
  label?: string | number
}

/** Accessible custom tooltip — label + value + unit, not color alone. */
export function CompareTooltip({
  active,
  payload,
  label,
  metric,
}: CompareTooltipProps) {
  if (!active || !payload?.length) {
    return null
  }

  return (
    <div className={styles.tooltip} role="status">
      <p className={styles.label}>{label}</p>
      <ul className={styles.list}>
        {payload.map((entry) => (
          <li key={String(entry.dataKey ?? entry.name)}>
            <span
              className={styles.swatch}
              style={{ background: entry.color ?? 'var(--color-accent)' }}
              aria-hidden
            />
            <span className={styles.name}>
              {entry.name ?? metricLabel(metric)}
            </span>
            <strong className={styles.value}>
              {typeof entry.value === 'number'
                ? entry.value.toFixed(1)
                : entry.value}{' '}
              {metricUnit(metric)}
            </strong>
          </li>
        ))}
      </ul>
    </div>
  )
}
