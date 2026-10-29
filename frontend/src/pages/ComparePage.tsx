import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchCompare, fetchDistricts } from '../api'
import { StatePanel } from '../components/StatePanel'
import { useCities } from '../hooks'
import type { WeatherMetric } from '../types'
import { formatLocalDateTime, getErrorMessage, metricLabel, metricUnit, toNumber } from '../utils'
import styles from './ComparePage.module.css'

const METRICS: WeatherMetric[] = ['temperature', 'humidity', 'wind_speed']
export function ComparePage() {
  const citiesQuery = useCities(); const [cityId, setCityId] = useState<number | null>(null); const [selectedIds, setSelectedIds] = useState<number[]>([]); const [metric, setMetric] = useState<WeatherMetric>('temperature'); const [submitted, setSubmitted] = useState<number[]>([])
  useEffect(() => { if (cityId == null && citiesQuery.data?.[0]) setCityId(citiesQuery.data[0].id) }, [citiesQuery.data, cityId])
  const districtsQuery = useQuery({ queryKey: ['districts', cityId], queryFn: () => fetchDistricts(cityId as number), enabled: cityId != null })
  const compareQuery = useQuery({ queryKey: ['compare', submitted, metric], queryFn: () => fetchCompare(submitted, metric), enabled: submitted.length >= 2 })
  const toggle = (id: number) => setSelectedIds((items) => items.includes(id) ? items.filter((value) => value !== id) : items.length < 5 ? [...items, id] : items)
  if (citiesQuery.isLoading) return <StatePanel title="Loading" message="Loading cities…" />
  if (citiesQuery.isError) return <StatePanel title="Error" message={getErrorMessage(citiesQuery.error)} tone="error" />
  const items = [...(compareQuery.data?.items ?? [])].sort((a, b) => toNumber(b.value) - toNumber(a.value))
  const sortedCities = [...(citiesQuery.data ?? [])].sort((a, b) => a.name.localeCompare(b.name))
  return <div className={styles.page}><header className={styles.intro}><h1>Compare localities</h1><p>Select 2–5 localities to compare current weather measurements.</p></header><section className={styles.controls}><label>City<select value={cityId ?? ''} onChange={(e) => { setCityId(Number(e.target.value)); setSelectedIds([]); setSubmitted([]) }}>{sortedCities.map((city) => <option key={city.id} value={city.id}>{city.name}</option>)}</select></label><fieldset className={styles.metricField}><legend>Metric</legend><div className={styles.metricTabs}>{METRICS.map((item) => <button key={item} type="button" className={metric === item ? styles.metricActive : styles.metricBtn} onClick={() => setMetric(item)}>{metricLabel(item)} <span>{metricUnit(item)}</span></button>)}</div></fieldset><button type="button" className={styles.compareBtn} onClick={() => setSubmitted(selectedIds)} disabled={selectedIds.length < 2}>Compare</button></section><section className={styles.districtPicker} aria-label="Locality selection"><div className={styles.pickerHead}><p className={styles.hint}>Selected: <strong>{selectedIds.length}/5</strong> (at least 2)</p><p className={styles.hint}>Total localities: {districtsQuery.data?.length ?? 0}</p></div><div className={styles.checkboxGrid}>{districtsQuery.data?.map((district) => <label key={district.id} className={selectedIds.includes(district.id) ? `${styles.checkItem} ${styles.checked}` : styles.checkItem}><input type="checkbox" checked={selectedIds.includes(district.id)} disabled={!selectedIds.includes(district.id) && selectedIds.length >= 5} onChange={() => toggle(district.id)} /><span>{district.name}</span></label>)}</div></section>{compareQuery.isLoading ? <StatePanel title="Loading" message="Calculating comparison…" /> : null}{compareQuery.isError ? <StatePanel title="Comparison error" message={getErrorMessage(compareQuery.error)} tone="error" /> : null}{compareQuery.isSuccess ? <section className={styles.tableCard}><h2>{metricLabel(metric)} comparison</h2><div className={styles.tableScroll}><table><thead><tr><th>Rank</th><th>Locality</th><th>{metricLabel(metric)} ({metricUnit(metric)})</th><th>Observed at</th></tr></thead><tbody>{items.map((item, index) => <tr key={item.district_id}><td>{index + 1}</td><td>{item.district_name}</td><td>{toNumber(item.value).toFixed(1)}</td><td>{formatLocalDateTime(item.observed_at)}</td></tr>)}</tbody></table></div></section> : null}</div>
}
