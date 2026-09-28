import { useState } from 'react'

import ErrorMessage from '../common/ErrorMessage'
import Button from '../ui/Button'
import { performJobAction } from '../../services/workerService'

const actions = [
  { id: 'accept', label: 'Accept job' },
  { id: 'reject', label: 'Reject job', variant: 'secondary' },
  { id: 'on-the-way', label: 'Start travelling / On the way', variant: 'secondary' },
  { id: 'in-progress', label: 'Start work / In progress', variant: 'secondary' },
  { id: 'resolved', label: 'Mark resolved', variant: 'success' },
]

export default function JobActions({ jobId, onActionComplete }) {
  const [loadingAction, setLoadingAction] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const runAction = async (action) => {
    setLoadingAction(action.id)
    setError('')
    setNotice('')

    try {
      await performJobAction(jobId, action.id)
      setNotice('The action was acknowledged by the service.')
      onActionComplete?.()
    } catch (actionError) {
      setError(actionError.message || 'This job action is currently unavailable.')
    } finally {
      setLoadingAction('')
    }
  }

  return (
    <section aria-labelledby="job-actions-heading" className="space-y-4">
      <div>
        <h3 id="job-actions-heading" className="text-lg font-semibold text-slate-950">Job actions</h3>
        <p className="mt-1 text-sm text-slate-600">Actions are confirmed by the worker service; this screen does not change job status locally.</p>
      </div>
      {error && <ErrorMessage message={error} />}
      {notice && <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800" role="status">{notice}</p>}
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <Button
            key={action.id}
            type="button"
            variant={action.variant || 'primary'}
            disabled={Boolean(loadingAction)}
            onClick={() => runAction(action)}
          >
            {loadingAction === action.id ? 'Sending...' : action.label}
          </Button>
        ))}
      </div>
    </section>
  )
}