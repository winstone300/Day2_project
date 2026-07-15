import { apiRequest } from './client'

export function getRegionSummary() {
  return apiRequest('/api/region/summary')
}

export function getRegionCategory(category, page = 1, district = '') {
  const params = new URLSearchParams({ page: String(page), size: '10' })
  if (district) params.set('district', district)
  return apiRequest(`/api/region/categories/${encodeURIComponent(category)}?${params}`)
}
