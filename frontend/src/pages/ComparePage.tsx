import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  fetchCompare,
  fetchDistricts,
  fetchHistory,
} from '../api'
import { CompareTooltip } from '../components/CompareTooltip'
import { StatePanel } from '../components/StatePanel'
import { useCities } from '../hooks'
import type { WeatherMetric } from '../types'
import {
  formatLocalDateTime,
  getErrorMessage,
  metricLabel,
  metricUnit,
  toNumber,
} from '../utils'
import { chartColor, readCssVar } from '../utils/chartTheme'
import styles from './ComparePage.module.css'

const METRICS: WeatherMetric[] = ['temperature', 'humidity', 'wind_speed']

function historyValue(
  metric: WeatherMetric,
  row: { temperature: string; humidity: number; wind_speed: string },
): number {
  if (metric === 'humidity') {
    return row.humidity
  }
  if (metric === 'wind_speed') {
    return toNumber(row.wind_speed)
  }
  return toNumber(row.temperature)
}

export function ComparePage() {
  const citiesQuery = useCities()
  const [cityId, setCityId] = useState<number | null>(null)
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [metric, setMetric] = useState<WeatherMetric>('temperature')
  const [submittedIds, setSubmittedIds] = useState<number[]>([])
  const [submittedMetric, setSubmittedMetric] =
    useState<WeatherMetric>('temperature')

  useEffect(() => {
    if (cityId == null && citiesQuery.data?.[0]) {
      setCityId(citiesQuery.data[0].id)
    }
  }, [citiesQuery.data, cityId])

  const districtsQuery = useQuery({
    queryKey: ['districts', cityId],
    queryFn: () => fetchDistricts(cityId as number),
    enabled: cityId != null,
  })

  const compareQuery = useQuery({
    queryKey: ['compare', submittedIds, submittedMetric],
    queryFn: () => fetchCompare(submittedIds, submittedMetric),
    enabled: submittedIds.length >= 2 && submittedIds.length <= 5,
  })

  const historyQuery = useQuery({
    queryKey: ['compare-history', submittedIds, submittedMetric],
    queryFn: async () => {
      const end = new Date()
      const start = new Date(end.getTime() - 24 * 60 * 60 * 1000)
      return Promise.all(
        submittedIds.map(async (id) => {
          const district = districtsQuery.data?.find((item) => item.id === id)
          const history = await fetchHistory(
            id,
            start.toISOString(),
            end.toISOString(),
          )
          return {
            districtId: id,
            districtName: district?.name ?? `İlçe ${id}`,
            history,
          }
        }),
      )
    },
    enabled: submittedIds.length >= 2 && !!districtsQuery.data,
  })

  const gridColor = readCssVar('--color-border', '#d5e2ee')
  const axisColor = readCssVar('--color-muted', '#5d738a')

  const barData = useMemo(() => {
    const items = [...(compareQuery.data?.items ?? [])].sort(
      (a, b) => toNumber(b.value) - toNumber(a.value),
    )
    return items.map((item, index) => ({
      name: item.district_name,
      value: toNumber(item.value),
      fill: chartColor(index),
      observed_at: item.observed_at,
    }))
  }, [compareQuery.data])

  const ranking = useMemo(() => {
    if (barData.length < 2) {
      return null
    }
    const highest = barData[0]
    const lowest = barData[barData.length - 1]
    return { highest, lowest }
  }, [barData])

  const lineData = useMemo(() => {
    if (!historyQuery.data) {
      return []
    }
    const timeMap = new Map<string, Record<string, string | number>>()
    for (const series of historyQuery.data) {
      for (const point of series.history) {
        const key = point.observed_at
        const row = timeMap.get(key) ?? {
          time: formatLocalDateTime(key),
          sortKey: key,
        }
        row[series.districtName] = historyValue(submittedMetric, point)
        timeMap.set(key, row)
      }
    }
    return Array.from(timeMap.values()).sort((a, b) =>
      String(a.sortKey).localeCompare(String(b.sortKey)),
    )
  }, [historyQuery.data, submittedMetric])

  const lineKeys = historyQuery.data?.map((item) => item.districtName) ?? []

  const toggleDistrict = (id: number) => {
    setSelectedIds((current) => {
      if (current.includes(id)) {
        return current.filter((value) => value !== id)
      }
      if (current.length >= 5) {
        return current
      }
      return [...current, id]
    })
  }

  const runCompare = () => {
    if (selectedIds.length < 2 || selectedIds.length > 5) {
      return
    }
    setSubmittedIds(selectedIds)
    setSubmittedMetric(metric)
  }

  if (citiesQuery.isLoading) {
    return <StatePanel title="Yükleniyor" message="Şehirler getiriliyor…" />
  }

  if (citiesQuery.isError) {
    return (
      <StatePanel
        title="Hata"
        message={getErrorMessage(citiesQuery.error)}
        tone="error"
      />
    )
  }

  return (
    <div className={styles.page}>
      <header className={styles.intro}>
        <h1>İlçe karşılaştırma</h1>
        <p>
          2–5 ilçe seçin. Çubuk grafik anlık farkı, alan grafik son 24 saati
          gösterir.
        </p>
      </header>

      <section className={styles.controls}>
        <label>
          Şehir
          <select
            value={cityId ?? ''}
            onChange={(event) => {
              setCityId(Number(event.target.value))
              setSelectedIds([])
              setSubmittedIds([])
            }}
          >
            {citiesQuery.data?.map((city) => (
              <option key={city.id} value={city.id}>
                {city.name}
              </option>
            ))}
          </select>
        </label>

        <fieldset className={styles.metricField}>
          <legend>Metrik</legend>
          <div className={styles.metricTabs}>
            {METRICS.map((item) => (
              <button
                key={item}
                type="button"
                className={
                  metric === item ? styles.metricActive : styles.metricBtn
                }
                onClick={() => setMetric(item)}
              >
                {metricLabel(item)}
                <span>{metricUnit(item)}</span>
              </button>
            ))}
          </div>
        </fieldset>

        <button
          type="button"
          className={styles.compareBtn}
          onClick={runCompare}
          disabled={selectedIds.length < 2 || selectedIds.length > 5}
        >
          Karşılaştır
        </button>
      </section>

      <section className={styles.districtPicker} aria-label="İlçe seçimi">
        <div className={styles.pickerHead}>
          <p className={styles.hint}>
            Seçili: <strong>{selectedIds.length}/5</strong> (en az 2)
          </p>
          <p className={styles.hint}>
            Toplam ilçe: {districtsQuery.data?.length ?? 0}
          </p>
        </div>
        <div className={styles.checkboxGrid}>
          {districtsQuery.data?.map((district) => {
            const checked = selectedIds.includes(district.id)
            const disabled = !checked && selectedIds.length >= 5
            return (
              <label
                key={district.id}
                className={
                  checked ? `${styles.checkItem} ${styles.checked}` : styles.checkItem
                }
              >
                <input
                  type="checkbox"
                  checked={checked}
                  disabled={disabled}
                  onChange={() => toggleDistrict(district.id)}
                />
                <span>{district.name}</span>
              </label>
            )
          })}
        </div>
      </section>

      {compareQuery.isLoading ? (
        <StatePanel title="Yükleniyor" message="Karşılaştırma hesaplanıyor…" />
      ) : null}

      {compareQuery.isError ? (
        <StatePanel
          title="Karşılaştırma hatası"
          message={getErrorMessage(compareQuery.error)}
          tone="error"
        />
      ) : null}

      {compareQuery.isSuccess ? (
        <>
          {ranking ? (
            <section className={styles.insights} aria-label="Öne çıkanlar">
              <article className={styles.insightHigh}>
                <span className={styles.insightLabel}>En yüksek</span>
                <strong>{ranking.highest.name}</strong>
                <span>
                  {ranking.highest.value.toFixed(1)}{' '}
                  {metricUnit(submittedMetric)}
                </span>
              </article>
              <article className={styles.insightLow}>
                <span className={styles.insightLabel}>En düşük</span>
                <strong>{ranking.lowest.name}</strong>
                <span>
                  {ranking.lowest.value.toFixed(1)}{' '}
                  {metricUnit(submittedMetric)}
                </span>
              </article>
            </section>
          ) : null}

          <section className={styles.chartCard} aria-label="Bar grafik">
            <div className={styles.chartHead}>
              <h2>
                {metricLabel(submittedMetric)} karşılaştırması
              </h2>
              <p>
                Değerler yüksekten düşüğe sıralanır · birim:{' '}
                {metricUnit(submittedMetric)}
              </p>
            </div>
            <div className={styles.chartWrap}>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart
                  data={barData}
                  margin={{ top: 12, right: 12, left: 4, bottom: 8 }}
                  barCategoryGap="28%"
                >
                  <defs>
                    {barData.map((item, index) => (
                      <linearGradient
                        key={item.name}
                        id={`barFill-${index}`}
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop offset="0%" stopColor={item.fill} stopOpacity={0.95} />
                        <stop offset="100%" stopColor={item.fill} stopOpacity={0.55} />
                      </linearGradient>
                    ))}
                  </defs>
                  <CartesianGrid
                    stroke={gridColor}
                    strokeDasharray="4 8"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: axisColor, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: axisColor, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    width={48}
                    label={{
                      value: metricUnit(submittedMetric),
                      angle: -90,
                      position: 'insideLeft',
                      fill: axisColor,
                      fontSize: 12,
                    }}
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(127,127,127,0.08)' }}
                    content={<CompareTooltip metric={submittedMetric} />}
                  />
                  <Bar
                    dataKey="value"
                    name={`${metricLabel(submittedMetric)} (${metricUnit(submittedMetric)})`}
                    radius={[12, 12, 4, 4]}
                    maxBarSize={64}
                  >
                    {barData.map((item, index) => (
                      <Cell key={item.name} fill={`url(#barFill-${index})`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ul className={styles.legendList} aria-label="İlçe renkleri">
              {barData.map((item) => (
                <li key={item.name}>
                  <span style={{ background: item.fill }} aria-hidden />
                  {item.name}: {item.value.toFixed(1)}{' '}
                  {metricUnit(submittedMetric)}
                </li>
              ))}
            </ul>
          </section>

          <section className={styles.chartCard} aria-label="Zaman serisi grafik">
            <div className={styles.chartHead}>
              <h2>Son 24 saat – {metricLabel(submittedMetric)}</h2>
              <p>
                Her çizgi bir ilçedir · birim: {metricUnit(submittedMetric)}
              </p>
            </div>
            {historyQuery.isLoading ? (
              <p className={styles.muted}>Geçmiş veriler yükleniyor…</p>
            ) : null}
            {historyQuery.isError ? (
              <StatePanel
                title="Geçmiş veri hatası"
                message={getErrorMessage(historyQuery.error)}
                tone="error"
              />
            ) : null}
            {historyQuery.isSuccess && lineData.length === 0 ? (
              <StatePanel
                title="Geçmiş kayıt yok"
                message="Seçilen ilçeler için son 24 saatte kayıt bulunamadı. Dashboard’dan Update Weather ile veri çekin."
                tone="empty"
              />
            ) : null}
            {historyQuery.isSuccess && lineData.length > 0 ? (
              <div className={styles.chartWrap}>
                <ResponsiveContainer width="100%" height={340}>
                  <AreaChart
                    data={lineData}
                    margin={{ top: 12, right: 12, left: 4, bottom: 8 }}
                  >
                    <defs>
                      {lineKeys.map((key, index) => (
                        <linearGradient
                          key={key}
                          id={`areaFill-${index}`}
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor={chartColor(index)}
                            stopOpacity={0.28}
                          />
                          <stop
                            offset="100%"
                            stopColor={chartColor(index)}
                            stopOpacity={0.02}
                          />
                        </linearGradient>
                      ))}
                    </defs>
                    <CartesianGrid
                      stroke={gridColor}
                      strokeDasharray="4 8"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="time"
                      tick={{ fill: axisColor, fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      minTickGap={28}
                    />
                    <YAxis
                      tick={{ fill: axisColor, fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      width={48}
                      label={{
                        value: metricUnit(submittedMetric),
                        angle: -90,
                        position: 'insideLeft',
                        fill: axisColor,
                        fontSize: 12,
                      }}
                    />
                    <Tooltip
                      content={<CompareTooltip metric={submittedMetric} />}
                    />
                    <Legend
                      verticalAlign="top"
                      height={36}
                      iconType="circle"
                      wrapperStyle={{ fontSize: 12 }}
                    />
                    {lineKeys.map((key, index) => (
                      <Area
                        key={key}
                        type="monotone"
                        dataKey={key}
                        name={`${key} (${metricUnit(submittedMetric)})`}
                        stroke={chartColor(index)}
                        strokeWidth={2.5}
                        fill={`url(#areaFill-${index})`}
                        dot={{ r: 3, strokeWidth: 0 }}
                        activeDot={{ r: 5 }}
                      />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            ) : null}
          </section>

          <section className={styles.tableCard} aria-label="Veri tablosu">
            <h2>Veri tablosu</h2>
            <div className={styles.tableScroll}>
              <table>
                <caption className={styles.srOnly}>
                  Seçilen ilçelerin {metricLabel(submittedMetric)} değerleri
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Sıra</th>
                    <th scope="col">İlçe</th>
                    <th scope="col">
                      {metricLabel(submittedMetric)} (
                      {metricUnit(submittedMetric)})
                    </th>
                    <th scope="col">Ölçüm zamanı</th>
                  </tr>
                </thead>
                <tbody>
                  {barData.map((item, index) => (
                    <tr key={item.name}>
                      <td>{index + 1}</td>
                      <td>
                        <span
                          className={styles.tableDot}
                          style={{ background: item.fill }}
                          aria-hidden
                        />
                        {item.name}
                      </td>
                      <td>{item.value.toFixed(1)}</td>
                      <td>{formatLocalDateTime(item.observed_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </div>
  )
}
