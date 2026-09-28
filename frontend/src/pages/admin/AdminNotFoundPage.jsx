import { Link } from 'react-router-dom'

import EmptyState from '../../components/common/EmptyState'

export default function AdminNotFoundPage() {
  return (
    <div className="space-y-5">
      <EmptyState title="Admin page not found" description="This admin route does not exist." />
      <Link className="inline-flex rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700" to="/admin">Return to admin dashboard</Link>
    </div>
  )
}