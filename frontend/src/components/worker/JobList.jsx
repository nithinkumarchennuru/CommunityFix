import { Link } from 'react-router-dom'

import EmptyState from '../common/EmptyState'
import PriorityBadge from './PriorityBadge'
import WorkerStatusBadge from './WorkerStatusBadge'
import { formatDate } from '../../utils/formatDate'

export default function JobList({ jobs }) {
  if (jobs.length === 0) {
    return <EmptyState title="No assigned jobs" description="Jobs assigned to your account will appear here." />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] border-collapse text-left text-sm">
        <caption className="sr-only">Jobs assigned to you</caption>
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <th scope="col" className="px-3 py-3 font-semibold">Job</th>
            <th scope="col" className="px-3 py-3 font-semibold">Category</th>
            <th scope="col" className="px-3 py-3 font-semibold">Priority</th>
            <th scope="col" className="px-3 py-3 font-semibold">Location</th>
            <th scope="col" className="px-3 py-3 font-semibold">Created</th>
            <th scope="col" className="px-3 py-3 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id} className="border-b border-slate-100 last:border-0">
              <td className="px-3 py-4">
                <Link className="font-semibold text-slate-900 hover:text-cyan-700" to={`/worker/jobs/${encodeURIComponent(job.id)}`}>
                  {job.title}
                </Link>
                <p className="mt-1 max-w-xs truncate text-xs text-slate-500">{job.description || 'Description unavailable'}</p>
              </td>
              <td className="px-3 py-4 text-slate-600">{job.category || 'Not provided'}</td>
              <td className="px-3 py-4"><PriorityBadge priority={job.priority} /></td>
              <td className="px-3 py-4 text-slate-600">{job.location || 'Not provided'}</td>
              <td className="px-3 py-4 whitespace-nowrap text-slate-600">{formatDate(job.createdAt)}</td>
              <td className="px-3 py-4"><WorkerStatusBadge status={job.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}