import { Link } from 'react-router-dom'
import type { CurrentWeatherItem } from '../types'
import { formatHumidity, formatLocalDateTime, formatTemperature, formatWind } from '../utils'
import styles from './DistrictCard.module.css'

export function DistrictCard({ item }: { item: CurrentWeatherItem }) {
  return <article className={styles.card} aria-label={`${item.district_name} weather`}>
    <header className={styles.header}><h3 className={styles.name}><Link to={`/districts/${item.district_id}`}>{item.district_name}</Link></h3><p className={styles.status}>{item.weather_status}</p></header>
    <p className={styles.temp}>{formatTemperature(item.temperature)}</p>
    <p className={styles.feels}>Feels like {item.feels_like != null ? formatTemperature(item.feels_like) : '—'}</p>
    <dl className={styles.meta}><div><dt>Humidity</dt><dd>{formatHumidity(item.humidity)}</dd></div><div><dt>Wind</dt><dd>{formatWind(item.wind_speed)}</dd></div></dl>
    {item.weather_description ? <p className={styles.description}>{item.weather_description}</p> : null}
    <p className={styles.updated}>Updated: {formatLocalDateTime(item.fetched_at)}</p>
  </article>
}
