const unavailableMessage = 'Worker and job APIs are not available in the backend yet. Connect these operations after the endpoint and response contract is documented.'

function unavailable() {
  return Promise.reject(new Error(unavailableMessage))
}

// Adapt documented backend payloads into the view models consumed by worker pages here.
export function getWorkerDashboard() {
  return unavailable()
}

export function getAvailability() {
  return unavailable()
}

export function updateAvailability(status) {
  void status
  return unavailable()
}

export function listAssignedJobs() {
  return unavailable()
}

export function getJobDetails(jobId) {
  void jobId
  return unavailable()
}

export function performJobAction(jobId, action) {
  void jobId
  void action
  return unavailable()
}