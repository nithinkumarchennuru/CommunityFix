import { Link, useParams } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import Loading from '../../components/common/Loading'
import ProblemStatusBadge from '../../components/resident/ProblemStatusBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import useResidentResource from '../../hooks/useResidentResource'
import { formatDate } from '../../utils/formatDate'

export default function ProblemDetailsPage() {
  const { problemId } = useParams()
  const { data: problem, loading, error, retry } = useResidentResource('problem', problemId)

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/resident/problems">Back to my problems</Link>
      {loading && <Loading message="Loading problem details..." />}
      {error && (
        <div className="space-y-3">
          <ErrorMessage message={error} />
          <Button variant="secondary" onClick={retry}>Try again</Button>
        </div>
      )}

      {!loading && !error && problem && (
        <>
          <header className="flex flex-col justify-between gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">Problem details</p>
              <h2 className="mt-2 text-3xl font-bold text-slate-950">{problem.title}</h2>
            </div>
            <ProblemStatusBadge status={problem.status} />
          </header>

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.6fr)_minmax(240px,1fr)]">
            <div className="space-y-5">
              <Card title="Description">
                <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{problem.description || 'No description provided.'}</p>
              </Card>

              {problem.photoUrl && (
                <Card title="Photo">
                  <img src={problem.photoUrl} alt={`Photo for ${problem.title}`} className="max-h-[28rem] w-full rounded-lg object-contain" />
                </Card>
              )}

              <Card title="Status history" subtitle="Updates provided for this report">
                {problem.statusHistory?.length ? (
                  <ol className="space-y-5">
                    {problem.statusHistory.map((entry, index) => (
                      <li key={`${entry.status}-${entry.createdAt}-${index}`} className="relative border-l-2 border-cyan-200 pl-5 last:border-transparent">
                        <span className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-cyan-700 ring-4 ring-white" />
                        <p className="font-semibold text-slate-900">{entry.status}</p>
                        {entry.note && <p className="mt-1 text-sm text-slate-600">{entry.note}</p>}
                        <p className="mt-1 text-xs text-slate-500">{formatDate(entry.createdAt)}</p>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="text-sm text-slate-600">No status updates have been provided.</p>
                )}
              </Card>
            </div>

            <aside className="space-y-5">
              <Card title="Report information">
                <dl className="space-y-4 text-sm">
                  <div><dt className="text-slate-500">Category</dt><dd className="mt-1 font-medium text-slate-900">{problem.category || 'Not provided'}</dd></div>
                  <div><dt className="text-slate-500">Priority</dt><dd className="mt-1 font-medium capitalize text-slate-900">{problem.priority || 'Not provided'}</dd></div>
                  <div><dt className="text-slate-500">Location</dt><dd className="mt-1 font-medium text-slate-900">{problem.location || 'Not provided'}</dd></div>
                  <div><dt className="text-slate-500">Created</dt><dd className="mt-1 font-medium text-slate-900">{formatDate(problem.createdAt)}</dd></div>
                </dl>
              </Card>

              {problem.assignedWorker && (
                <Card title="Assigned worker">
                  <p className="text-sm font-medium text-slate-900">{problem.assignedWorker.name || 'Worker assigned'}</p>
                </Card>
              )}
            </aside>
          </div>
        </>
      )}
    </div>
  )
}