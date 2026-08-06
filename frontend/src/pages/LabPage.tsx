import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  postFilter,
  postSeventhElement,
  postStatistics,
} from '../api'
import { StatePanel } from '../components/StatePanel'
import { getErrorMessage, parseNumberList } from '../utils'
import styles from './LabPage.module.css'

type LabAction = 'seventh' | 'statistics' | 'filter'

export function LabPage() {
  const [rawValues, setRawValues] = useState('12, 18, 21, 24, 27, 29, 31, 33')
  const [minimum, setMinimum] = useState('20')
  const [lastRequest, setLastRequest] = useState<unknown>(null)
  const [lastResponse, setLastResponse] = useState<unknown>(null)
  const [localError, setLocalError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: async (action: LabAction) => {
      const values = parseNumberList(rawValues)
      if (action === 'seventh') {
        const body = { values }
        setLastRequest({ path: 'POST /exercises/seventh-element', body })
        return postSeventhElement(values)
      }
      if (action === 'statistics') {
        const body = { values }
        setLastRequest({ path: 'POST /exercises/statistics', body })
        return postStatistics(values)
      }
      const min = Number(minimum)
      if (Number.isNaN(min)) {
        throw new Error('Minimum değer sayı olmalı')
      }
      const body = { values }
      setLastRequest({
        path: `POST /exercises/filter?minimum=${min}`,
        body,
      })
      return postFilter(values, min)
    },
    onSuccess: (data) => {
      setLocalError(null)
      setLastResponse(data)
    },
    onError: (error) => {
      setLastResponse(null)
      setLocalError(getErrorMessage(error))
    },
  })

  const run = (action: LabAction) => {
    try {
      setLocalError(null)
      mutation.mutate(action)
    } catch (error) {
      setLocalError(getErrorMessage(error))
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.intro}>
        <h1>Eğitim / API laboratuvarı</h1>
        <p>
          JSON istek gövdesi oluşturup eğitim endpoint’lerini çağırın. Python
          listelerinde indeks 0’dan başlar; 7. elemanın indeksi 6’dır.
        </p>
      </header>

      <section className={styles.formCard}>
        <label>
          Sayı dizisi
          <textarea
            value={rawValues}
            onChange={(event) => setRawValues(event.target.value)}
            rows={4}
            spellCheck={false}
          />
        </label>

        <label>
          Filtre minimum değeri
          <input
            type="number"
            value={minimum}
            onChange={(event) => setMinimum(event.target.value)}
          />
        </label>

        <div className={styles.actions}>
          <button
            type="button"
            disabled={mutation.isPending}
            onClick={() => run('seventh')}
          >
            7. elemanı bul
          </button>
          <button
            type="button"
            disabled={mutation.isPending}
            onClick={() => run('statistics')}
          >
            İstatistik hesapla
          </button>
          <button
            type="button"
            disabled={mutation.isPending}
            onClick={() => run('filter')}
          >
            Filtrele
          </button>
        </div>
      </section>

      {localError ? (
        <StatePanel title="İstek hatası" message={localError} tone="error" />
      ) : null}

      <section className={styles.ioGrid}>
        <article>
          <h2>Gönderilen istek</h2>
          <pre>{lastRequest ? JSON.stringify(lastRequest, null, 2) : '—'}</pre>
        </article>
        <article>
          <h2>API yanıtı</h2>
          <pre>
            {lastResponse ? JSON.stringify(lastResponse, null, 2) : '—'}
          </pre>
        </article>
      </section>
    </div>
  )
}
