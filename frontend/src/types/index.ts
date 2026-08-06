/** Shared TypeScript types mirroring FastAPI response models. */

export interface City {
  id: number
  name: string
  country_code: string
  latitude: string | null
  longitude: string | null
  created_at: string
}

export interface CurrentWeatherItem {
  district_id: number
  district_name: string
  temperature: string
  feels_like: string | null
  humidity: number
  wind_speed: string
  weather_status: string
  weather_description: string | null
  provider: string
  observed_at: string
  fetched_at: string
}

export interface ExtremeDistrict {
  district_id: number
  district_name: string
  value: string
}

export interface WeatherSummary {
  city_id: number
  district_count: number
  average_temperature: string
  average_humidity: string
  last_updated_at: string
  hottest: ExtremeDistrict
  coldest: ExtremeDistrict
  most_humid: ExtremeDistrict
  windiest: ExtremeDistrict
}

export interface WeatherFetchResult {
  successful: number
  failed: number
  skipped_duplicates: number
  errors: Array<{ district_id: number; message: string }>
  records: unknown[]
}

export type WeatherMetric = 'temperature' | 'humidity' | 'wind_speed'

export interface District {
  id: number
  city_id: number
  name: string
  latitude: string
  longitude: string
  created_at: string
}

export interface WeatherRecord {
  id: number
  district_id: number
  temperature: string
  feels_like: string | null
  humidity: number
  wind_speed: string
  weather_status: string
  weather_description: string | null
  provider: string
  observed_at: string
  fetched_at: string
}

export interface CompareItem {
  district_id: number
  district_name: string
  metric: WeatherMetric
  value: string
  observed_at: string
}

export interface CompareResponse {
  metric: WeatherMetric
  items: CompareItem[]
}

export interface SeventhElementResponse {
  value: number
  index: number
  position: number
}

export interface StatisticsResponse {
  count: number
  minimum: number
  maximum: number
  total: number
  average: number
}

export interface FilterResponse {
  minimum: number
  original_count: number
  filtered_count: number
  values: number[]
}

export interface ApiErrorBody {
  detail?:
    | string
    | {
        code?: string
        message?: string
      }
    | Array<{ msg?: string }>
}
