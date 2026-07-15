import { apiRequest } from './client'

export function sendChatMessage(message, maxResults = 3) {
  return apiRequest('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      max_results: maxResults,
    }),
  })
}
