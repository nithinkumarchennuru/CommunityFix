import { Link, useParams } from 'react-router-dom'

import AdminRequestState from '../../components/admin/AdminRequestState'
import WorkerStatusBadge from '../../components/worker/WorkerStatusBadge'
import Card from '../../components/ui/Card'
import useAdminResource from '../../hooks/useAdminResource'
import { formatDate } from '../../utils/formatDate'

export default function AdminWorkerDetailsPage() {
  const { workerId } = useParams()
  const { data: worker, loading, error, retry } = useAdminResource('worker', workerId)

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/admin/workers">Back to workers</Link>
      <AdminRequestState loading={loading} error={error} retry={retry} empty={!loading && !error && !worker} emptyTitle="Worker not found" emptyDescription="No worker details were returned for this route.">
        {worker && <><header><p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">Worker details</p><h2 className="mt-2 text-3xl font-bold text-slate-950">{worker.name || 'Name unavailable'}</h2></header><Card title="Worker information"><dl className="grid gap-5 sm:grid-cols-2 text-sm"><div><dt className="text-slate-500">Email</dt><dd className="mt-1 text-slate-900">{worker.email || 'Not provided'}</dd></div><div><dt className="text-slate-500">Phone</dt><dd className="mt-1 text-slate-900">{worker.phone || 'Not provided'}</dd></div><div><dt className="text-slate-500">Availability</dt><dd className="mt-1"><WorkerStatusBadge status={worker.availability} /></dd></div><div><dt className="text-slate-500">Status</dt><dd className="mt-1"><WorkerStatusBadge status={worker.status} /></dd></div><div><dt className="text-slate-500">Created</dt><dd className="mt-1 text-slate-900">{formatDate(worker.createdAt)}</dd></div></dl></Card></>}
      </AdminRequestState>
    </div>
  )
}