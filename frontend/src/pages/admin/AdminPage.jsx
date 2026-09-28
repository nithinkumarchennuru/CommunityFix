import { Link } from 'react-router-dom'

import AdminRequestState from '../../components/admin/AdminRequestState'
import Card from '../../components/ui/Card'
import useAdminResource from '../../hooks/useAdminResource'

const summaryItems = [
  { key: 'issueCount', label: 'Community issues', href: '/admin/issues' },
  { key: 'jobCount', label: 'Jobs', href: '/admin/issues' },
  { key: 'userCount', label: 'Users and residents', href: '/admin/users' },
  { key: 'workerCount', label: 'Workers', href: '/admin/workers' },
]

export default function AdminPage() {
  const { data, loading, error, retry } = useAdminResource('dashboard')

  return (
    <div className="space-y-8">
      <header className="flex flex-col justify-between gap-5 border-b border-slate-200 pb-7 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">Administration</p>
          <h2 className="mt-2 text-3xl font-bold text-slate-950">Community overview</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">Review community records and operational information provided by the admin service.</p>
        </div>
        <Link to="/admin/issues" className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">Manage issues and jobs</Link>
      </header>

      <AdminRequestState loading={loading} error={error} retry={retry}>
        {!data ? (
          <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-600">Dashboard summary is unavailable until the admin API provides it.</p>
        ) : (
          <section aria-label="Community summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {summaryItems.map(({ key, label, href }) => (
              <Card key={key} className="border-t-4 border-t-cyan-700">
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <p className="mt-3 text-3xl font-bold text-slate-950">{Number.isFinite(data[key]) ? data[key] : 'Unavailable'}</p>
                <Link className="mt-3 inline-block text-sm font-semibold text-cyan-800 hover:text-cyan-950" to={href}>View records</Link>
              </Card>
            ))}
          </section>
        )}
      </AdminRequestState>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold text-slate-950">Management</h3>
        <div className="flex flex-wrap gap-3">
          <Link to="/admin/issues" className="inline-flex items-center justify-center rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition-colors hover:bg-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">Issues and jobs</Link>
          <Link to="/admin/workers" className="inline-flex items-center justify-center rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition-colors hover:bg-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">Workers</Link>
          <Link to="/admin/users" className="inline-flex items-center justify-center rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition-colors hover:bg-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">Users and residents</Link>
        </div>
      </section>
    </div>
  )
}
