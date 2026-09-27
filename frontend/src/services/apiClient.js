const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

export { API_BASE_URL }

export async function apiClient(endpoint, options = {}) {
  const { method = 'GET', headers = {}, body, ...rest } = options

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...rest,
  })

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json().catch(() => null)
    : await response.text().catch(() => null)

  if (!response.ok) {
    const message = payload?.message || payload?.error || `Request failed with status ${response.status}`
    throw new Error(message)
  }

  return payload
}
