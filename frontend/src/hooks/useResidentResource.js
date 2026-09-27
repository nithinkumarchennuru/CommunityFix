import { useEffect, useState } from 'react'

import { getProblemDetails, listMyProblems } from '../services/residentService'

export default function useResidentResource(resource, problemId = null) {
  const [state, setState] = useState({ data: null, loading: true, error: '' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let isCurrent = true
    const request = resource === 'problem'
      ? getProblemDetails(problemId)
      : listMyProblems()

    request
      .then((data) => {
        if (isCurrent) {
          setState({ data, loading: false, error: '' })
        }
      })
      .catch((error) => {
        if (isCurrent) {
          setState({ data: null, loading: false, error: error.message || 'Unable to load resident problems.' })
        }
      })

    return () => {
      isCurrent = false
    }
  }, [resource, problemId, attempt])

  const retry = () => {
    setState((current) => ({ ...current, loading: true, error: '' }))
    setAttempt((current) => current + 1)
  }

  return { ...state, retry }
}