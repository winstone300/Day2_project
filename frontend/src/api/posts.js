import { apiRequest } from './client'

export function getPosts({ page = 1, size = 10, query = '', sort = 'latest' } = {}) {
  const params = new URLSearchParams({
    page: String(page),
    size: String(size),
    sort,
  })
  if (query.trim()) {
    params.set('query', query.trim())
  }
  return apiRequest(`/api/posts?${params}`)
}

export function getPost(postId) {
  return apiRequest(`/api/posts/${postId}`)
}

export function createPost(payload) {
  return apiRequest('/api/posts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function verifyPostPassword(postId, editPassword) {
  return apiRequest(`/api/posts/${postId}/verify-password`, {
    method: 'POST',
    body: JSON.stringify({ edit_password: editPassword }),
  })
}

export function updatePost(postId, payload) {
  return apiRequest(`/api/posts/${postId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deletePost(postId, editPassword) {
  return apiRequest(`/api/posts/${postId}`, {
    method: 'DELETE',
    body: JSON.stringify({ edit_password: editPassword }),
  })
}
