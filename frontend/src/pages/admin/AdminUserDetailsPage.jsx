import { Link, useParams } from 'react-router-dom'

import AdminRequestState from '../../components/admin/AdminRequestState'
import Card from '../../components/ui/Card'
import useAdminResource from '../../hooks/useAdminResource'
import { formatDate } from '../../utils/formatDate'

export default function AdminUserDetailsPage() {
  const { userId } = useParams()
  const { data: user, loading, error, retry } = useAdminResource('user', userId)

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/admin/users">Back to users</Link>
      <AdminRequestState loading={loading} error={error} retry={retry} empty={!loading && !error && !user} emptyTitle="User not found" emptyDescription="No user details were returned for this route.">
        {user && <><header><p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">User details</p><h2 className="mt-2 text-3xl font-bold text-slate-950">{user.name || 'Name unavailable'}</h2></header><Card title="Account information"><dl className="grid gap-5 sm:grid-cols-2 text-sm"><div><dt className="text-slate-500">Email</dt><dd className="mt-1 text-slate-900">{user.email || 'Not provided'}</dd></div><div><dt className="text-slate-500">Role</dt><dd className="mt-1 text-slate-900">{user.role || 'Not provided'}</dd></div><div><dt className="text-slate-500">Status</dt><dd className="mt-1 text-slate-900">{user.status || 'Status unavailable'}</dd></div><div><dt className="text-slate-500">Created</dt><dd className="mt-1 text-slate-900">{formatDate(user.createdAt)}</dd></div></dl></Card></>}
      </AdminRequestState>
    </div>
  )
}