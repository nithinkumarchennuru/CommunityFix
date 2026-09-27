const unavailableMessage = 'Resident problem APIs are not available in the backend yet. Connect these operations after the endpoint and response contract is documented.'

function unavailable() {
  return Promise.reject(new Error(unavailableMessage))
}

// Adapt documented backend payloads into the view models consumed by resident pages here.
export function listMyProblems() {
  return unavailable()
}

export function getProblemDetails(problemId) {
  void problemId
  return unavailable()
}

export function createProblem(problem) {
  void problem
  return unavailable()
}