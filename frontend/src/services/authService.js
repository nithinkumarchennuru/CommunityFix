import { apiClient } from './apiClient'

const endpoints = {
  login: import.meta.env.VITE_AUTH_LOGIN_ENDPOINT,
  register: import.meta.env.VITE_AUTH_REGISTER_ENDPOINT,
  logout: import.meta.env.VITE_AUTH_LOGOUT_ENDPOINT,
}

function getEndpoint(operation) {
  const endpoint = endpoints[operation]?.trim()

  if (!endpoint) {
    throw new Error(`Authentication ${operation} endpoint is not configured.`)
  }

  return endpoint
}

export function login(credentials) {
  return apiClient(getEndpoint('login'), { method: 'POST', body: credentials })
}

export function register(details) {
  return apiClient(getEndpoint('register'), { method: 'POST', body: details })
}

export function logout() {
  const endpoint = endpoints.logout?.trim()

  if (!endpoint) {
    return Promise.resolve(null)
  }

  return apiClient(endpoint, { method: 'POST' })
}