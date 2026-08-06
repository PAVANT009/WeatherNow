import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchCities,
  fetchCityWeather,
  fetchCurrentWeather,
  fetchWeatherSummary,
} from '../api'

export const queryKeys = {
  cities: ['cities'] as const,
  current: (cityId: number) => ['weather', 'current', cityId] as const,
  summary: (cityId: number) => ['weather', 'summary', cityId] as const,
}

export function useCities() {
  return useQuery({
    queryKey: queryKeys.cities,
    queryFn: fetchCities,
  })
}

export function useCurrentWeather(cityId: number | null) {
  return useQuery({
    queryKey: queryKeys.current(cityId ?? 0),
    queryFn: () => fetchCurrentWeather(cityId as number),
    enabled: cityId != null,
  })
}

export function useWeatherSummary(cityId: number | null) {
  return useQuery({
    queryKey: queryKeys.summary(cityId ?? 0),
    queryFn: () => fetchWeatherSummary(cityId as number),
    enabled: cityId != null,
    retry: false,
  })
}

export function useFetchCityWeather(cityId: number | null) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => {
      if (cityId == null) {
        return Promise.reject(new Error('Şehir seçilmedi'))
      }
      return fetchCityWeather(cityId)
    },
    onSuccess: async () => {
      if (cityId == null) {
        return
      }
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.current(cityId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.summary(cityId) }),
      ])
    },
  })
}
