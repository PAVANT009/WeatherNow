import { useEffect, useMemo, useState } from 'react'
import { DistrictCard } from '../components/DistrictCard'
import { StatePanel } from '../components/StatePanel'
import {
  useCities,
  useCurrentWeather,
  useFetchCityWeather,
  useWeatherSummary,
} from '../hooks'
import { getErrorMessage } from '../utils'
import {
  formatHumidity,
  formatLocalDateTime,
  formatTemperature,
  formatWind,
} from '../utils/format'
import styles from './DashboardPage.module.css'

export function DashboardPage() {
  const citiesQuery = useCities()
  const [cityId, setCityId] = useState<number | null>(null)
  const [query, setQuery] = useState('')

  useEffect(() => {
    if (cityId != null) {
      return
    }
    const first = citiesQuery.data?.[0]
    if (first) {
      setCityId(first.id)
    }
  }, [citiesQuery.data, cityId])

  const currentQuery = useCurrentWeather(cityId)
  const summaryQuery = useWeatherSummary(cityId)
  const fetchMutation = useFetchCityWeather(cityId)

  const selectedCity = citiesQuery.data?.find((city) => city.id === cityId)

  const filteredDistricts = useMemo(() => {
    const items = currentQuery.data ?? []
    const q = query.trim().toLowerCase()
    if (!q) {
      return items
    }
    return items.filter((item) =>
      item.district_name.toLowerCase().includes(q),
    )
  }, [currentQuery.data, query])

  const hero = filteredDistricts[0] ?? currentQuery.data?.[0] ?? null

  const handleRefresh = () => {
    if (cityId == null || fetchMutation.isPending) {
      return
    }
    fetchMutation.mutate()
  }

  if (citiesQuery.isLoading) {
    return (
      <StatePanel
        title="Yükleniyor"
        message="Şehir listesi getiriliyor…"
        tone="info"
      />
    )
  }

  if (citiesQuery.isError) {
    return (
      <StatePanel
        title="Şehirler alınamadı"
        message={getErrorMessage(citiesQuery.error)}
        tone="error"
      />
    )
  }

  if (!citiesQuery.data?.length) {
    return (
      <StatePanel
        title="Şehir bulunamadı"
        message="Veritabanında şehir yok. Backend seed komutunu çalıştırın."
        tone="empty"
      />
    )
  }

  return (
    <div className={styles.dashboard}>
      <section className={styles.controls} aria-label="Konum ve güncelleme">
        <div className={styles.filters}>
          <label className={styles.label}>
            Ülke
            <select className={styles.select} value="TR" disabled>
              <option value="TR">Türkiye</option>
            </select>
          </label>

          <span className={styles.sep}>/</span>

          <label className={styles.label} htmlFor="city-select">
            Şehir
            <select
              id="city-select"
              className={styles.select}
              value={cityId ?? ''}
              onChange={(event) => setCityId(Number(event.target.value))}
            >
              {citiesQuery.data.map((city) => (
                <option key={city.id} value={city.id}>
                  {city.name}
                </option>
              ))}
            </select>
          </label>

          <label className={styles.label} htmlFor="district-search">
            İlçe ara
            <input
              id="district-search"
              className={styles.search}
              type="search"
              placeholder="Search district"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>

          <div className={styles.unitToggle} aria-label="Sıcaklık birimi">
            <span className={styles.unitActive}>°C</span>
            <span className={styles.unitInactive} title="Yakında">
              °F
            </span>
          </div>
        </div>

        <div className={styles.actions}>
          {summaryQuery.data ? (
            <span className={styles.updatedLabel}>
              Last updated:{' '}
              {formatLocalDateTime(summaryQuery.data.last_updated_at)}
            </span>
          ) : null}
          <button
            type="button"
            className={styles.refresh}
            onClick={handleRefresh}
            disabled={cityId == null || fetchMutation.isPending}
          >
            <span className="material-symbols-outlined">sync</span>
            {fetchMutation.isPending ? 'Updating…' : 'Update Weather'}
          </button>
        </div>
      </section>

      {fetchMutation.isError ? (
        <StatePanel
          title="Güncelleme başarısız"
          message={getErrorMessage(fetchMutation.error)}
          tone="error"
        />
      ) : null}

      {fetchMutation.isSuccess ? (
        <p className={styles.fetchNote} role="status">
          {selectedCity?.name} için {fetchMutation.data.successful} ilçe
          kaydedildi
          {fetchMutation.data.failed > 0
            ? `, ${fetchMutation.data.failed} başarısız`
            : ''}
          {fetchMutation.data.skipped_duplicates > 0
            ? `, ${fetchMutation.data.skipped_duplicates} tekrar atlandı`
            : ''}
          .
        </p>
      ) : null}

      {hero ? (
        <section className={styles.hero} aria-label="Şehir özeti">
          <div className={styles.heroScrim} />
          <div className={styles.heroContent}>
            <div className={styles.heroText}>
              <div className={styles.heroBadges}>
                <span className={styles.liveBadge}>Live Observation</span>
                <span className={styles.heroDate}>
                  {formatLocalDateTime(hero.observed_at)}
                </span>
              </div>
              <h2 className={styles.heroCity}>
                {selectedCity?.name ?? 'Şehir'}
              </h2>
              <div className={styles.heroTempRow}>
                <p className={styles.heroTemp}>
                  {Number(hero.temperature).toFixed(0)}°
                </p>
                <div>
                  <p className={styles.heroStatus}>{hero.weather_status}</p>
                  <p className={styles.heroFeels}>
                    Feels like:{' '}
                    {hero.feels_like != null
                      ? formatTemperature(hero.feels_like)
                      : '—'}
                  </p>
                </div>
              </div>
              <div className={styles.heroMeta}>
                <div>
                  <span className="material-symbols-outlined">
                    humidity_percentage
                  </span>
                  <span className={styles.metaLabel}>Humidity</span>
                  <strong>{formatHumidity(hero.humidity)}</strong>
                </div>
                <div>
                  <span className="material-symbols-outlined">air</span>
                  <span className={styles.metaLabel}>Wind</span>
                  <strong>{formatWind(hero.wind_speed)}</strong>
                </div>
                <div>
                  <span className="material-symbols-outlined">location_on</span>
                  <span className={styles.metaLabel}>Sample district</span>
                  <strong>{hero.district_name}</strong>
                </div>
              </div>
            </div>
            <div className={styles.heroVisual} aria-hidden>
              <div className={styles.glow} />
              <span className={`material-symbols-outlined ${styles.heroIcon}`}>
                partly_cloudy_day
              </span>
            </div>
          </div>
        </section>
      ) : null}

      {summaryQuery.isSuccess ? (
        <section className={styles.summary} aria-label="Özet">
          <article className={styles.summaryCard}>
            <h2>
              <span className="material-symbols-outlined">local_fire_department</span>
              Warmest
            </h2>
            <p className={styles.summaryValue}>
              {summaryQuery.data.hottest.district_name}
            </p>
            <p>{formatTemperature(summaryQuery.data.hottest.value)}</p>
          </article>
          <article className={styles.summaryCard}>
            <h2>
              <span className="material-symbols-outlined">ac_unit</span>
              Coolest
            </h2>
            <p className={styles.summaryValue}>
              {summaryQuery.data.coldest.district_name}
            </p>
            <p>{formatTemperature(summaryQuery.data.coldest.value)}</p>
          </article>
          <article className={styles.summaryCard}>
            <h2>
              <span className="material-symbols-outlined">water_drop</span>
              Most humid
            </h2>
            <p className={styles.summaryValue}>
              {summaryQuery.data.most_humid.district_name}
            </p>
            <p>{formatHumidity(summaryQuery.data.most_humid.value)}</p>
          </article>
          <article className={styles.summaryCard}>
            <h2>
              <span className="material-symbols-outlined">air</span>
              Windiest
            </h2>
            <p className={styles.summaryValue}>
              {summaryQuery.data.windiest.district_name}
            </p>
            <p>{formatWind(summaryQuery.data.windiest.value)}</p>
          </article>
        </section>
      ) : null}

      {summaryQuery.isError && !currentQuery.isLoading ? (
        <StatePanel
          title="Özet yok"
          message="Bu şehir için henüz hava kaydı yok. «Update Weather» ile Open-Meteo’dan çekebilirsiniz."
          tone="empty"
        />
      ) : null}

      {currentQuery.isLoading ? (
        <StatePanel
          title="Yükleniyor"
          message="İlçe hava durumları getiriliyor…"
          tone="info"
        />
      ) : null}

      {currentQuery.isError ? (
        <StatePanel
          title="Hava verisi alınamadı"
          message={getErrorMessage(currentQuery.error)}
          tone="error"
        />
      ) : null}

      {currentQuery.isSuccess && currentQuery.data.length === 0 ? (
        <StatePanel
          title="Kayıt yok"
          message="Seçili şehir için güncel hava kaydı bulunamadı. Verileri güncellemeyi deneyin."
          tone="empty"
        />
      ) : null}

      {currentQuery.isSuccess && filteredDistricts.length === 0 && query ? (
        <StatePanel
          title="Sonuç yok"
          message={`«${query}» ile eşleşen ilçe bulunamadı.`}
          tone="empty"
        />
      ) : null}

      {filteredDistricts.length > 0 ? (
        <section
          className={styles.grid}
          aria-label={`${selectedCity?.name ?? 'Şehir'} ilçe kartları`}
        >
          {filteredDistricts.map((item) => (
            <DistrictCard key={item.district_id} item={item} />
          ))}
        </section>
      ) : null}
    </div>
  )
}
