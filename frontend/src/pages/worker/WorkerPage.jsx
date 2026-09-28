import { Link } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import EmptyState from '../../components/common/EmptyState'
import Loading from '../../components/common/Loading'
import WorkerStatusBadge from '../../components/worker/WorkerStatusBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import useWorkerResource from '../../hooks/useWorkerResource'

const summaryCards = [
  { key: 'activeJobsCount', label: 'Active jobs', detail: 'Count provided by the service' },
  { key: 'pendingJobsCount', label: 'Pending jobs', detail: 'Count provided by the service' },
  { key: 'assignedJobsCount', label: 'Assigned jobs', detail: 'Count provided by the service' },
]

export default function WorkerPage() {
  const { data: dashboard, loading, error, retry } = useWorkerResource('dashboard')

  return (
    <div className="space-y-8">
      <section className="flex flex-col justify-between gap-5 border-b border-slate-200 pb-7 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Worker home</p>
          <h2 className="mt-2 text-3xl font-bold text-slate-950">Your work, at a glance.</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">Review jobs assigned to you and the availability reported by the worker service.</p>
        </div>
        <Link to="/worker/jobs" className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">View assigned jobs</Link>
      </section>

      <section aria-label="Worker overview" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="border-t-4 border-t-emerald-700">
          <p className="text-sm font-medium text-slate-500">Availability</p>
          <div className="mt-3"><WorkerStatusBadge status={dashboard?.availabilityStatus} /></div>
          <Link to="/worker/availability" className="mt-3 inline-block text-sm font-semibold text-cyan-800 hover:text-cyan-950">Manage availability</Link>
        </Card>
        {summaryCards.map(({ key, label, detail }) => (
          <Card key={key}>
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className="mt-3 text-3xl font-bold text-slate-950">{dashboard?.[key] ?? '—'}</p>
            <p className="mt-1 text-xs text-slate-500">{detail}</p>
          </Card>
        ))}
      </section>

      {loading && <Loading message="Loading your worker dashboard..." />}
      {error && (
        <div className="space-y-3">
          <ErrorMessage message={error} />
          <Button variant="secondary" onClick={retry}>Try again</Button>
        </div>
      )}

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-semibold text-slate-950">Assigned jobs</h3>
            <p className="mt-1 text-sm text-slate-600">Job counts and assignments are supplied by the worker service.</p>
          </div>
          <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/worker/jobs">My jobs</Link>
        </div>
        {!loading && !error && (!Array.isArray(dashboard?.recentJobs) || dashboard.recentJobs.length === 0) && (
          <EmptyState title="No recent jobs to show" description="No recent assignments were included in the worker dashboard response." />
        )}
        {!loading && !error && Array.isArray(dashboard?.recentJobs) && dashboard.recentJobs.length > 0 && (
          <Card>
            <ul className="divide-y divide-slate-100">
              {dashboard.recentJobs.slice(0, 3).map((job) => (
                <li key={job.id} className="flex flex-wrap items-center justify-between gap-3 py-4 first:pt-0 last:pb-0">
                  <div>
                    <Link className="font-semibold text-slate-900 hover:text-cyan-700" to={`/worker/jobs/${encodeURIComponent(job.id)}`}>{job.title}</Link>
                    <p className="mt-1 text-sm text-slate-600">{job.location || 'Location not provided'}</p>
                  </div>
                  <WorkerStatusBadge status={job.status} />
                </li>
              ))}
            </ul>
          </Card>
        )}
      </section>
    </div>
  )
}
