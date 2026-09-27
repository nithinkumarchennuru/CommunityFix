import { Link } from 'react-router-dom'

import EmptyState from '../common/EmptyState'
import ProblemStatusBadge from './ProblemStatusBadge'
import { formatDate } from '../../utils/formatDate'

export default function ProblemList({ problems }) {
  if (problems.length === 0) {
    return <EmptyState title="No problems reported" description="When you report a community problem, it will appear here." />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[680px] border-collapse text-left text-sm">
        <caption className="sr-only">Problems reported by you</caption>
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <th scope="col" className="px-3 py-3 font-semibold">Problem</th>
            <th scope="col" className="px-3 py-3 font-semibold">Category</th>
            <th scope="col" className="px-3 py-3 font-semibold">Priority</th>
            <th scope="col" className="px-3 py-3 font-semibold">Reported</th>
            <th scope="col" className="px-3 py-3 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody>
          {problems.map((problem) => (
            <tr key={problem.id} className="border-b border-slate-100 last:border-0">
              <td className="px-3 py-4">
                <Link className="font-semibold text-slate-900 hover:text-cyan-700" to={`/resident/problems/${encodeURIComponent(problem.id)}`}>
                  {problem.title}
                </Link>
              </td>
              <td className="px-3 py-4 text-slate-600">{problem.category || 'Not provided'}</td>
              <td className="px-3 py-4 capitalize text-slate-600">{problem.priority || 'Not provided'}</td>
              <td className="px-3 py-4 whitespace-nowrap text-slate-600">{formatDate(problem.createdAt)}</td>
              <td className="px-3 py-4"><ProblemStatusBadge status={problem.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}