import { useEffect, useState } from 'react'

import {
  getAdminDashboard,
  getIssueDetails,
  getUserDetails,
  getWorkerDetails,
  listIssues,
  listUsers,
  listWorkers,
} from '../services/adminService'

const requests = {
  dashboard: () => getAdminDashboard(),
  issues: () => listIssues(),
  issue: (id) => getIssueDetails(id),
  workers: () => listWorkers(),
  worker: (id) => getWorkerDetails(id),
  users: () => listUsers(),
  user: (id) => getUserDetails(id),
}

export default function useAdminResource(resource, itemId = null) {
  const [state, setState] = useState({ key: '', data: null, loading: true, error: '' })
  const [attempt, setAttempt] = useState(0)
  const key = `${resource}:${itemId ?? ''}`
  const isKnownResource = Object.hasOwn(requests, resource)

  useEffect(() => {
    let isCurrent = true
    const request = requests[resource]

    if (!request) return undefined

    request(itemId)
      .then((data) => {
        if (isCurrent) setState({ key, data, loading: false, error: '' })
      })
      .catch((error) => {
        if (isCurrent) {
          setState({ key, data: null, loading: false, error: error.message || 'Unable to load admin data.' })
        }
      })

    return () => {
      isCurrent = false
    }
  }, [resource, itemId, attempt, key])

  const retry = () => {
    setState((current) => ({ ...current, loading: true, error: '' }))
    setAttempt((current) => current + 1)
  }

  if (!isKnownResource) {
    return { data: null, loading: false, error: 'Unknown admin resource.', retry }
  }

  if (state.key !== key) {
    return { data: null, loading: true, error: '', retry }
  }

  return { ...state, retry }
}