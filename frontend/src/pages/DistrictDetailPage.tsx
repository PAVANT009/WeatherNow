import { useMemo } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { fetchDistrictCurrent, fetchHistory } from '../api'
import { StatePanel } from '../components/StatePanel'
import {
  formatHumidity,
  formatLocalDateTime,
  formatTemperature,
  formatWind,
  getErrorMessage,
  toNumber,
} from '../utils'
import styles from './DistrictDetailPage.module.css'

export function DistrictDetailPage() {
  const params = useParams()
  const districtId = Number(params.districtId)

  const currentQuery = useQuery({
    queryKey: ['district-current', districtId],
    queryFn: () => fetchDistrictCurrent(districtId),
    enabled: Number.isFinite(districtId) && districtId > 0,
  })

  const historyQuery = useQuery({
    queryKey: ['district-history', districtId],
    queryFn: () => {
      const end = new Date()
      const start = new Date(end.getTime() - 24 * 60 * 60 * 1000)
      return fetchHistory(districtId, start.toISOString(), end.toISOString())
    },
    enabled: Number.isFinite(districtId) && districtId > 0,
  })

  const chartData = useMemo(
    () =>
      (historyQuery.data ?? []).map((row) => ({
        time: formatLocalDateTime(row.observed_at),
        temperature: toNumber(row.temperature),
        humidity: row.humidity,
        wind: toNumber(row.wind_speed),
      })),
    [historyQuery.data],
  )

  if (!Number.isFinite(districtId) || districtId <= 0) {
    return (
      <StatePanel
        title="Geçersiz ilçe"
        message="URL içindeki ilçe kimliği geçersiz."
        tone="error"
      />
    )
  }

  if (currentQuery.isLoading) {
    return (
      <StatePanel title="Yükleniyor" message="İlçe hava durumu getiriliyor…" />
    )
  }

  if (currentQuery.isError) {
    return (
      <StatePanel
        title="İlçe verisi alınamadı"
        message={getErrorMessage(currentQuery.error)}
        tone="error"
      />
    )
  }

  const item = currentQuery.data
  if (!item) {
    return null
  }

  return (
    <div className={styles.page}>
      <p className={styles.back}>
        <Link to="/">← Dashboard</Link>
      </p>

      <header className={styles.hero}>
        <div>
          <h1>{item.district_name}</h1>
          <p className={styles.status}>{item.weather_status}</p>
        </div>
        <p className={styles.temp}>{formatTemperature(item.temperature)}</p>
      </header>

      <section className={styles.stats} aria-label="Güncel değerler">
        <article>
          <h2>Hissedilen</h2>
          <p>
            {item.feels_like != null
              ? formatTemperature(item.feels_like)
              : '—'}
          </p>
        </article>
        <article>
          <h2>Nem</h2>
          <p>{formatHumidity(item.humidity)}</p>
        </article>
        <article>
          <h2>Rüzgâr</h2>
          <p>{formatWind(item.wind_speed)}</p>
        </article>
        <article>
          <h2>Son veri</h2>
          <p>{formatLocalDateTime(item.fetched_at)}</p>
        </article>
      </section>

      <section className={styles.chartCard}>
        <h2>Son 24 saat – sıcaklık (°C)</h2>
        {historyQuery.isLoading ? <p>Geçmiş yükleniyor…</p> : null}
        {historyQuery.isError ? (
          <StatePanel
            title="Geçmiş alınamadı"
            message={getErrorMessage(historyQuery.error)}
            tone="error"
          />
        ) : null}
        {historyQuery.isSuccess && chartData.length === 0 ? (
          <StatePanel
            title="Kayıt yok"
            message="Bu ilçe için son 24 saatte kayıt bulunamadı."
            tone="empty"
          />
        ) : null}
        {chartData.length > 0 ? (
          <div className={styles.chartWrap}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis
                  yAxisId="left"
                  label={{ value: '°C', angle: -90, position: 'insideLeft' }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  label={{ value: '% / km/h', angle: 90, position: 'insideRight' }}
                />
                <Tooltip />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="temperature"
                  name="Sıcaklık (°C)"
                  stroke="#1f6fad"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="humidity"
                  name="Nem (%)"
                  stroke="#0e8a6c"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="wind"
                  name="Rüzgâr (km/h)"
                  stroke="#c47b16"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : null}
      </section>
    </div>
  )
}
