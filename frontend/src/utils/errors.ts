import axios from 'axios'
import type { ApiErrorBody } from '../types'

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) return 'Unable to connect to the server. Is the backend running?'
    const detail = (error.response.data as ApiErrorBody | undefined)?.detail
    if (detail && typeof detail === 'object' && !Array.isArray(detail) && detail.message) return detail.message
    if (typeof detail === 'string' && detail.trim()) return detail
    if (error.response.status === 404) return 'The requested record was not found.'
    if (error.response.status === 422) return 'The submitted data is invalid.'
    if ([502, 503].includes(error.response.status)) return 'The service is temporarily unavailable. Please try again.'
    return `Request failed (HTTP ${error.response.status}).`
  }
  return error instanceof Error && error.message ? error.message : 'An unexpected error occurred.'
}
