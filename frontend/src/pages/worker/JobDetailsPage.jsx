import { Link, useParams } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import Loading from '../../components/common/Loading'
import JobActions from '../../components/worker/JobActions'
import PriorityBadge from '../../components/worker/PriorityBadge'
import WorkerStatusBadge from '../../components/worker/WorkerStatusBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import useWorkerResource from '../../hooks/useWorkerResource'
import { formatDate } from '../../utils/formatDate'

export default function JobDetailsPage() {
  const { jobId } = useParams()
  const { data: job, loading, error, retry } = useWorkerResource('job', jobId)

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/worker/jobs">Back to my jobs</Link>
      {loading && <Loading message="Loading job details..." />}
      {error && (
        <div className="space-y-3">
          <ErrorMessage message={error} />
          <Button variant="secondary" onClick={retry}>Try again</Button>
        </div>
      )}

      {!loading && !error && job && (
        <>
          <header className="flex flex-col justify-between gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Assigned job</p>
              <h2 className="mt-2 text-3xl font-bold text-slate-950">{job.title}</h2>
            </div>
            <WorkerStatusBadge status={job.status} />
          </header>

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.6fr)_minmax(240px,1fr)]">
            <div className="space-y-5">
              <Card title="Problem description">
                <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{job.description || 'Description not provided.'}</p>
              </Card>

              {job.photoUrl && (
                <Card title="Photo">
                  <img src={job.photoUrl} alt={`Photo for ${job.title}`} className="max-h-[28rem] w-full rounded-lg object-contain" />
                </Card>
              )}

              <Card title="Status history" subtitle="Updates are shown only when supplied by the worker service.">
                {job.statusHistory?.length ? (
                  <ol className="space-y-5">
                    {job.statusHistory.map((entry, index) => (
                      <li key={`${entry.status}-${entry.createdAt}-${index}`} className="relative border-l-2 border-cyan-200 pl-5 last:border-transparent">
                        <span className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-cyan-700 ring-4 ring-white" />
                        <p className="font-semibold text-slate-900">{entry.status}</p>
                        {entry.note && <p className="mt-1 text-sm text-slate-600">{entry.note}</p>}
                        <p className="mt-1 text-xs text-slate-500">{formatDate(entry.createdAt)}</p>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="text-sm text-slate-600">No status history was provided.</p>
                )}
              </Card>

              <JobActions jobId={jobId} onActionComplete={retry} />
            </div>

            <aside className="space-y-5">
              <Card title="Job information">
                <dl className="space-y-4 text-sm">
                  <div><dt className="text-slate-500">Category</dt><dd className="mt-1 font-medium text-slate-900">{job.category || 'Not provided'}</dd></div>
                  <div><dt className="text-slate-500">Priority</dt><dd className="mt-1"><PriorityBadge priority={job.priority} /></dd></div>
                  <div><dt className="text-slate-500">Location</dt><dd className="mt-1 font-medium text-slate-900">{job.location || 'Not provided'}</dd></div>
                  <div><dt className="text-slate-500">Created</dt><dd className="mt-1 font-medium text-slate-900">{formatDate(job.createdAt)}</dd></div>
                </dl>
              </Card>

              {job.resident && (
                <Card title="Resident information">
                  {job.resident.name && <p className="text-sm font-medium text-slate-900">{job.resident.name}</p>}
                  {job.resident.contact && <p className="mt-1 text-sm text-slate-600">{job.resident.contact}</p>}
                  {job.resident.description && <p className="mt-2 text-sm text-slate-600">{job.resident.description}</p>}
                </Card>
              )}

              {job.assignment && (
                <Card title="Assignment information">
                  <dl className="space-y-3 text-sm">
                    {job.assignment.assignedAt && <div><dt className="text-slate-500">Assigned</dt><dd className="mt-1 text-slate-900">{formatDate(job.assignment.assignedAt)}</dd></div>}
                    {job.assignment.status && <div><dt className="text-slate-500">Assignment status</dt><dd className="mt-1 text-slate-900">{job.assignment.status}</dd></div>}
                  </dl>
                </Card>
              )}
            </aside>
          </div>
        </>
      )}
    </div>
  )
}