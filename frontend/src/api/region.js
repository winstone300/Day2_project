import { apiRequest } from './client'

export function getRegionSummary() {
  return apiRequest('/api/region/summary')
}
