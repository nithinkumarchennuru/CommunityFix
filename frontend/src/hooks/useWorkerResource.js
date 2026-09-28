import { useEffect, useState } from 'react'

import {
  getAvailability,
  getJobDetails,
  getWorkerDashboard,
  listAssignedJobs,
} from '../services/workerService'

const requests = {
  dashboard: () => getWorkerDashboard(),
  availability: () => getAvailability(),
  jobs: () => listAssignedJobs(),
  job: (jobId) => getJobDetails(jobId),
}

export default function useWorkerResource(resource, jobId = null) {
  const [state, setState] = useState({ key: '', data: null, loading: true, error: '' })
  const [attempt, setAttempt] = useState(0)
  const isKnownResource = Object.hasOwn(requests, resource)
  const key = `${resource}:${jobId ?? ''}`

  useEffect(() => {
    let isCurrent = true
    const request = requests[resource]

    if (!request) {
      return undefined
    }

    request(jobId)
      .then((data) => {
        if (isCurrent) {
          setState({ key, data, loading: false, error: '' })
        }
      })
      .catch((error) => {
        if (isCurrent) {
          setState({ key, data: null, loading: false, error: error.message || 'Unable to load worker information.' })
        }
      })

    return () => {
      isCurrent = false
    }
  }, [resource, jobId, attempt, key])

  const retry = () => {
    setState((current) => ({ ...current, loading: true, error: '' }))
    setAttempt((current) => current + 1)
  }

  if (!isKnownResource) {
    return { data: null, loading: false, error: 'Unknown worker resource.', retry }
  }

  if (state.key !== key) {
    return { data: null, loading: true, error: '', retry }
  }

  return { ...state, retry }
}