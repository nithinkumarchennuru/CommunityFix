const unavailableMessage = 'Admin data APIs are not available in the backend yet. Connect these operations after the endpoint and response contract is documented.'

function unavailable() {
  return Promise.reject(new Error(unavailableMessage))
}

function validateId(id, entity) {
  if (typeof id !== 'string' || !id.trim()) {
    return Promise.reject(new Error(`A valid ${entity} ID is required.`))
  }

  return id.trim()
}

// Map documented backend responses into Admin page view models here when APIs exist.
export function getAdminDashboard() {
  return unavailable()
}

export function listIssues() {
  return unavailable()
}

export function getIssueDetails(issueId) {
  const validId = validateId(issueId, 'issue')
  return typeof validId === 'string' ? unavailable() : validId
}

export function listWorkers() {
  return unavailable()
}

export function getWorkerDetails(workerId) {
  const validId = validateId(workerId, 'worker')
  return typeof validId === 'string' ? unavailable() : validId
}

export function listUsers() {
  return unavailable()
}

export function getUserDetails(userId) {
  const validId = validateId(userId, 'user')
  return typeof validId === 'string' ? unavailable() : validId
}