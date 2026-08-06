import { Link } from 'react-router-dom'
import type { CurrentWeatherItem } from '../types'
import {
  formatHumidity,
  formatLocalDateTime,
  formatTemperature,
  formatWind,
} from '../utils'
import styles from './DistrictCard.module.css'

interface DistrictCardProps {
  item: CurrentWeatherItem
}

export function DistrictCard({ item }: DistrictCardProps) {
  return (
    <article className={styles.card} aria-label={`${item.district_name} hava durumu`}>
      <header className={styles.header}>
        <h3 className={styles.name}>
          <Link to={`/districts/${item.district_id}`}>{item.district_name}</Link>
        </h3>
        <p className={styles.status}>{item.weather_status}</p>
      </header>

      <p className={styles.temp}>{formatTemperature(item.temperature)}</p>
      <p className={styles.feels}>
        Hissedilen{' '}
        {item.feels_like != null
          ? formatTemperature(item.feels_like)
          : '—'}
      </p>

      <dl className={styles.meta}>
        <div>
          <dt>Nem</dt>
          <dd>{formatHumidity(item.humidity)}</dd>
        </div>
        <div>
          <dt>Rüzgâr</dt>
          <dd>{formatWind(item.wind_speed)}</dd>
        </div>
      </dl>

      {item.weather_description ? (
        <p className={styles.description}>{item.weather_description}</p>
      ) : null}

      <p className={styles.updated}>
        Güncellendi: {formatLocalDateTime(item.fetched_at)}
      </p>
    </article>
  )
}
