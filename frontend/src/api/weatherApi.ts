import { apiClient } from './client'
import type {
  City,
  CompareResponse,
  CurrentWeatherItem,
  District,
  FilterResponse,
  SeventhElementResponse,
  StatisticsResponse,
  WeatherFetchResult,
  WeatherMetric,
  WeatherRecord,
  WeatherSummary,
} from '../types'

export async function fetchCities(): Promise<City[]> {
  const { data } = await apiClient.get<City[]>('/cities')
  return data
}

export async function fetchDistricts(cityId: number): Promise<District[]> {
  const { data } = await apiClient.get<District[]>(
    `/cities/${cityId}/districts`,
  )
  return data
}

export async function fetchCurrentWeather(
  cityId: number,
): Promise<CurrentWeatherItem[]> {
  const { data } = await apiClient.get<CurrentWeatherItem[]>('/weather/current', {
    params: { city_id: cityId },
  })
  return data
}

export async function fetchDistrictCurrent(
  districtId: number,
): Promise<CurrentWeatherItem> {
  const { data } = await apiClient.get<CurrentWeatherItem>(
    `/weather/current/${districtId}`,
  )
  return data
}

export async function fetchWeatherSummary(
  cityId: number,
): Promise<WeatherSummary> {
  const { data } = await apiClient.get<WeatherSummary>('/weather/summary', {
    params: { city_id: cityId },
  })
  return data
}

export async function fetchCityWeather(
  cityId: number,
): Promise<WeatherFetchResult> {
  const { data } = await apiClient.post<WeatherFetchResult>(
    `/weather/fetch/${cityId}`,
  )
  return data
}

export async function fetchCompare(
  districtIds: number[],
  metric: WeatherMetric,
): Promise<CompareResponse> {
  const { data } = await apiClient.get<CompareResponse>('/weather/compare', {
    params: {
      district_ids: districtIds.join(','),
      metric,
    },
  })
  return data
}

export async function fetchHistory(
  districtId: number,
  startDate: string,
  endDate: string,
): Promise<WeatherRecord[]> {
  const { data } = await apiClient.get<WeatherRecord[]>(
    `/weather/history/${districtId}`,
    {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    },
  )
  return data
}

export async function postSeventhElement(
  values: number[],
): Promise<SeventhElementResponse> {
  const { data } = await apiClient.post<SeventhElementResponse>(
    '/exercises/seventh-element',
    { values },
  )
  return data
}

export async function postStatistics(
  values: number[],
): Promise<StatisticsResponse> {
  const { data } = await apiClient.post<StatisticsResponse>(
    '/exercises/statistics',
    { values },
  )
  return data
}

export async function postFilter(
  values: number[],
  minimum: number,
): Promise<FilterResponse> {
  const { data } = await apiClient.post<FilterResponse>(
    '/exercises/filter',
    { values },
    { params: { minimum } },
  )
  return data
}
