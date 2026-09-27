import { apiClient } from './apiClient'

export async function getHealth() {
  return apiClient('/api/health')
}

export async function pingApi() {
  return apiClient('/api/ping')
}

export async function testDatabaseConnection() {
  return apiClient('/api/db/test')
}
