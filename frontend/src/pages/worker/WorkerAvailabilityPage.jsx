import { useState } from 'react'
import { Link } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import Loading from '../../components/common/Loading'
import WorkerStatusBadge from '../../components/worker/WorkerStatusBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import useWorkerResource from '../../hooks/useWorkerResource'
import { updateAvailability } from '../../services/workerService'

const availabilityOptions = ['AVAILABLE', 'BUSY', 'OFFLINE', 'ON_LEAVE', 'AT_CAPACITY']

export default function WorkerAvailabilityPage() {
  const { data, loading, error, retry } = useWorkerResource('availability')
  const [selection, setSelection] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [notice, setNotice] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!selection) return

    setSaving(true)
    setSaveError('')
    setNotice('')

    try {
      await updateAvailability(selection)
      setNotice('Availability update was accepted. Refreshing the current value...')
      retry()
    } catch (updateError) {
      setSaveError(updateError.message || 'Availability could not be updated.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <header>
        <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/worker">Worker dashboard</Link>
        <p className="mt-5 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Worker settings</p>
        <h2 className="mt-2 text-3xl font-bold text-slate-950">Availability</h2>
        <p className="mt-2 text-sm text-slate-600">Availability is displayed and updated only through the worker service.</p>
      </header>

      <Card title="Current availability" subtitle="The value below is supplied by the backend when available.">
        {loading && <Loading message="Loading availability..." />}
        {error && (
          <div className="space-y-3">
            <ErrorMessage message={error} />
            <Button variant="secondary" onClick={retry}>Try again</Button>
          </div>
        )}
        {!loading && !error && <WorkerStatusBadge status={data?.status} />}
      </Card>

      <Card title="Request a status change" subtitle="No workload or capacity calculations are performed in the frontend.">
        {saveError && <div className="mb-4"><ErrorMessage message={saveError} /></div>}
        {notice && <p className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800" role="status">{notice}</p>}
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label htmlFor="availability" className="block text-sm font-medium text-slate-700">Availability status</label>
            <select id="availability" name="availability" value={selection} onChange={(event) => setSelection(event.target.value)} required className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100">
              <option value="">Choose a status</option>
              {availabilityOptions.map((status) => <option key={status} value={status}>{status.replaceAll('_', ' ')}</option>)}
            </select>
          </div>
          <Button type="submit" disabled={!selection || saving}>{saving ? 'Updating...' : 'Update availability'}</Button>
        </form>
      </Card>
    </div>
  )
}