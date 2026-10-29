import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { postFilter, postSeventhElement, postStatistics } from '../api'
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
  const mutation = useMutation({ mutationFn: async (action: LabAction) => {
    const values = parseNumberList(rawValues)
    if (action === 'seventh') { const body = { values }; setLastRequest({ path: 'POST /exercises/seventh-element', body }); return postSeventhElement(values) }
    if (action === 'statistics') { const body = { values }; setLastRequest({ path: 'POST /exercises/statistics', body }); return postStatistics(values) }
    const min = Number(minimum); if (Number.isNaN(min)) throw new Error('Minimum value must be a number')
    const body = { values }; setLastRequest({ path: `POST /exercises/filter?minimum=${min}`, body }); return postFilter(values, min)
  }, onSuccess: (data) => { setLocalError(null); setLastResponse(data) }, onError: (error) => { setLastResponse(null); setLocalError(getErrorMessage(error)) } })
  return <div className={styles.page}><header className={styles.intro}><h1>Learning / API Lab</h1><p>Create JSON request bodies and call the learning endpoints. Python list indexes start at 0, so the seventh item has index 6.</p></header><section className={styles.formCard}><label>Number list<textarea value={rawValues} onChange={(e) => setRawValues(e.target.value)} rows={4} spellCheck={false} /></label><label>Minimum filter value<input type="number" value={minimum} onChange={(e) => setMinimum(e.target.value)} /></label><div className={styles.actions}><button type="button" disabled={mutation.isPending} onClick={() => mutation.mutate('seventh')}>Find seventh item</button><button type="button" disabled={mutation.isPending} onClick={() => mutation.mutate('statistics')}>Calculate statistics</button><button type="button" disabled={mutation.isPending} onClick={() => mutation.mutate('filter')}>Filter</button></div></section>{localError ? <StatePanel title="Request error" message={localError} tone="error" /> : null}<section className={styles.ioGrid}><article><h2>Request sent</h2><pre>{lastRequest ? JSON.stringify(lastRequest, null, 2) : '—'}</pre></article><article><h2>API response</h2><pre>{lastResponse ? JSON.stringify(lastResponse, null, 2) : '—'}</pre></article></section></div>
}
