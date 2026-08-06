import axios from 'axios'

const baseURL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ||
  'http://localhost:8000/api/v1'

/**
 * Single Axios instance for all WeatherNow API calls.
 * Frontend never talks to Open-Meteo directly.
 */
export const apiClient = axios.create({
  baseURL,
  timeout: 20000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})
