import axios from 'axios'
import type { ApiErrorBody } from '../types'

/** Convert Axios/unknown errors into short user-facing Turkish messages. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return 'Sunucuya bağlanılamadı. Backend ve PostgreSQL çalışıyor mu?'
    }

    const status = error.response.status
    const body = error.response.data as ApiErrorBody | undefined
    const detail = body?.detail

    if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
      if (detail.message) {
        return detail.message
      }
    }

    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }

    if (status === 404) {
      return 'İstenen kayıt bulunamadı.'
    }
    if (status === 422) {
      return 'Gönderilen veriler geçersiz.'
    }
    if (status === 502 || status === 503) {
      return 'Servis geçici olarak kullanılamıyor. Lütfen tekrar deneyin.'
    }

    return `İstek başarısız oldu (HTTP ${status}).`
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return 'Beklenmeyen bir hata oluştu.'
}
