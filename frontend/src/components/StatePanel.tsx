import styles from './StatePanel.module.css'

interface StatePanelProps {
  title: string
  message: string
  tone?: 'info' | 'error' | 'empty'
}

export function StatePanel({
  title,
  message,
  tone = 'info',
}: StatePanelProps) {
  return (
    <div className={`${styles.panel} ${styles[tone]}`} role="status">
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.message}>{message}</p>
    </div>
  )
}
