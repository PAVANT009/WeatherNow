import type { ReactNode } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useTheme } from '../theme/ThemeContext'
import styles from './AppLayout.module.css'

interface AppLayoutProps {
  children: ReactNode
}

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: 'dashboard', end: true },
  { to: '/compare', label: 'Compare Districts', icon: 'compare_arrows', end: false },
  { to: '/lab', label: 'API Lab', icon: 'terminal', end: false },
] as const

function pageTitle(pathname: string): { title: string; subtitle: string } {
  if (pathname.startsWith('/compare')) {
    return {
      title: 'Compare Districts',
      subtitle: 'Compare live weather metrics across districts',
    }
  }
  if (pathname.startsWith('/districts/')) {
    return {
      title: 'District Details',
      subtitle: 'Current conditions and recent history',
    }
  }
  if (pathname.startsWith('/lab')) {
    return {
      title: 'API Lab',
      subtitle: 'Exercise endpoints with JSON request/response',
    }
  }
  return {
    title: 'Weather Dashboard',
    subtitle: 'Compare live weather conditions across districts',
  }
}

export function AppLayout({ children }: AppLayoutProps) {
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const { title, subtitle } = pageTitle(location.pathname)
  const nowLabel = new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date())

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar} aria-label="Ana gezinti">
        <div className={styles.brandRow}>
          <span className={`material-symbols-outlined ${styles.brandIcon}`}>
            partly_cloudy_day
          </span>
          <span className={styles.brand}>WeatherNow</span>
        </div>

        <nav className={styles.nav}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? `${styles.navLink} ${styles.active}` : styles.navLink
              }
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className={styles.liveBox}>
          <div className={styles.liveRow}>
            <span className={styles.liveDot} aria-hidden />
            <span className={styles.liveLabel}>Live data</span>
          </div>
          <span className={styles.liveMeta}>Backend + Open-Meteo</span>
        </div>
      </aside>

      <div className={styles.content}>
        <header className={styles.topbar}>
          <div>
            <h1 className={styles.pageTitle}>{title}</h1>
            <p className={styles.pageSubtitle}>{subtitle}</p>
          </div>

          <div className={styles.topActions}>
            <button
              type="button"
              className={styles.themeToggle}
              onClick={toggleTheme}
              aria-label={
                theme === 'night'
                  ? 'Gündüz moduna geç'
                  : 'Gece moduna geç'
              }
              title={theme === 'night' ? 'Day mode' : 'Night mode'}
            >
              <span className="material-symbols-outlined">
                {theme === 'night' ? 'light_mode' : 'dark_mode'}
              </span>
            </button>
            <div className={styles.clock}>
              <span>{nowLabel}</span>
            </div>
          </div>
        </header>

        <main className={styles.main}>{children}</main>
      </div>
    </div>
  )
}
