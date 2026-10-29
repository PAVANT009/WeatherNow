import { useMemo } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchDistrictCurrent, fetchHistory } from '../api'
import { StatePanel } from '../components/StatePanel'
import { formatHumidity, formatLocalDateTime, formatTemperature, formatWind, getErrorMessage, toNumber } from '../utils'
import styles from './DistrictDetailPage.module.css'

export function DistrictDetailPage() {
  const districtId = Number(useParams().districtId)
  const currentQuery = useQuery({ queryKey: ['district-current', districtId], queryFn: () => fetchDistrictCurrent(districtId), enabled: Number.isFinite(districtId) && districtId > 0 })
  const historyQuery = useQuery({ queryKey: ['district-history', districtId], queryFn: () => { const end = new Date(); return fetchHistory(districtId, new Date(end.getTime() - 86400000).toISOString(), end.toISOString()) }, enabled: Number.isFinite(districtId) && districtId > 0 })
  const chartData = useMemo(() => (historyQuery.data ?? []).map((row) => ({ time: formatLocalDateTime(row.observed_at), temperature: toNumber(row.temperature), humidity: row.humidity, wind: toNumber(row.wind_speed) })), [historyQuery.data])
  if (!Number.isFinite(districtId) || districtId <= 0) return <StatePanel title="Invalid locality" message="The locality ID in the URL is invalid." tone="error" />
  if (currentQuery.isLoading) return <StatePanel title="Loading" message="Loading local weather…" />
  if (currentQuery.isError) return <StatePanel title="Could not load locality" message={getErrorMessage(currentQuery.error)} tone="error" />
  const item = currentQuery.data; if (!item) return null
  return <div className={styles.page}><p className={styles.back}><Link to="/">← Dashboard</Link></p><header className={styles.hero}><div><h1>{item.district_name}</h1><p className={styles.status}>{item.weather_status}</p></div><p className={styles.temp}>{formatTemperature(item.temperature)}</p></header><section className={styles.stats} aria-label="Current conditions"><article><h2>Feels like</h2><p>{item.feels_like != null ? formatTemperature(item.feels_like) : '—'}</p></article><article><h2>Humidity</h2><p>{formatHumidity(item.humidity)}</p></article><article><h2>Wind</h2><p>{formatWind(item.wind_speed)}</p></article><article><h2>Last update</h2><p>{formatLocalDateTime(item.fetched_at)}</p></article></section><section className={styles.chartCard}><h2>Last 24 hours – temperature (°C)</h2>{historyQuery.isLoading ? <p>Loading history…</p> : null}{historyQuery.isError ? <StatePanel title="Could not load history" message={getErrorMessage(historyQuery.error)} tone="error" /> : null}{historyQuery.isSuccess && !chartData.length ? <StatePanel title="No records" message="No weather records are available for this locality in the last 24 hours." tone="empty" /> : null}{chartData.length > 0 ? <div className={styles.chartWrap}><ResponsiveContainer width="100%" height={300}><LineChart data={chartData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="time" /><YAxis yAxisId="left" label={{ value: '°C', angle: -90, position: 'insideLeft' }} /><YAxis yAxisId="right" orientation="right" label={{ value: '% / km/h', angle: 90, position: 'insideRight' }} /><Tooltip /><Legend /><Line yAxisId="left" type="monotone" dataKey="temperature" name="Temperature (°C)" stroke="#1f6fad" strokeWidth={2} dot={false} /><Line yAxisId="right" type="monotone" dataKey="humidity" name="Humidity (%)" stroke="#0e8a6c" strokeWidth={2} dot={false} /><Line yAxisId="right" type="monotone" dataKey="wind" name="Wind (km/h)" stroke="#c47b16" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer></div> : null}</section></div>
}
