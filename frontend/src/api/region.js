import { apiRequest } from './client'

export function getRegionSummary() {
  return apiRequest('/api/region/summary')
}

export function getRegionCategory(category, page = 1) {
  const params = new URLSearchParams({ page: String(page), size: '10' })
  return apiRequest(`/api/region/categories/${encodeURIComponent(category)}?${params}`)
}
