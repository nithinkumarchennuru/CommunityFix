import { Link, useParams } from 'react-router-dom'

import AdminRequestState from '../../components/admin/AdminRequestState'
import ProblemStatusBadge from '../../components/resident/ProblemStatusBadge'
import PriorityBadge from '../../components/worker/PriorityBadge'
import Card from '../../components/ui/Card'
import useAdminResource from '../../hooks/useAdminResource'
import { formatDate } from '../../utils/formatDate'

export default function AdminIssueDetailsPage() {
  const { issueId } = useParams()
  const { data: issue, loading, error, retry } = useAdminResource('issue', issueId)

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/admin/issues">Back to issues and jobs</Link>
      <AdminRequestState loading={loading} error={error} retry={retry} empty={!loading && !error && !issue} emptyTitle="Issue not found" emptyDescription="No issue details were returned for this route." >
        {issue && (
          <>
            <header className="flex flex-col justify-between gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start">
              <div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">Issue details</p><h2 className="mt-2 text-3xl font-bold text-slate-950">{issue.title || 'Title unavailable'}</h2></div>
              <ProblemStatusBadge status={issue.status} />
            </header>
            <div className="grid gap-5 lg:grid-cols-[minmax(0,1.5fr)_minmax(240px,1fr)]">
              <div className="space-y-5">
                <Card title="Description"><p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{issue.description || 'Description not provided.'}</p></Card>
                {issue.photoUrl && <Card title="Photo"><img src={issue.photoUrl} alt={`Photo for ${issue.title || 'community issue'}`} className="max-h-[28rem] w-full rounded-lg object-contain" /></Card>}
                {Array.isArray(issue.statusHistory) && <Card title="Status history"><ol className="space-y-3">{issue.statusHistory.map((entry, index) => <li key={`${entry.status}-${entry.createdAt}-${index}`} className="border-l-2 border-cyan-200 pl-4"><p className="font-medium text-slate-900">{entry.status || 'Status unavailable'}</p><p className="text-xs text-slate-500">{formatDate(entry.createdAt)}</p>{entry.note && <p className="mt-1 text-sm text-slate-600">{entry.note}</p>}</li>)}</ol></Card>}
              </div>
              <Card title="Issue information"><dl className="space-y-4 text-sm"><div><dt className="text-slate-500">Category</dt><dd className="mt-1 text-slate-900">{issue.category || 'Not provided'}</dd></div><div><dt className="text-slate-500">Priority</dt><dd className="mt-1"><PriorityBadge priority={issue.priority} /></dd></div><div><dt className="text-slate-500">Location</dt><dd className="mt-1 text-slate-900">{issue.location || 'Not provided'}</dd></div><div><dt className="text-slate-500">Created</dt><dd className="mt-1 text-slate-900">{formatDate(issue.createdAt)}</dd></div></dl></Card>
            </div>
          </>
        )}
      </AdminRequestState>
    </div>
  )
}