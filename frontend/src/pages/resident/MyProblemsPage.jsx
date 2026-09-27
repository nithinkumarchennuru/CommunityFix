import { Link } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import Loading from '../../components/common/Loading'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import ProblemList from '../../components/resident/ProblemList'
import useResidentResource from '../../hooks/useResidentResource'

export default function MyProblemsPage() {
  const { data: problems, loading, error, retry } = useResidentResource('problems')

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/resident">Resident dashboard</Link>
          <h2 className="mt-4 text-3xl font-bold text-slate-950">My problems</h2>
          <p className="mt-2 text-sm text-slate-600">Review reports you have submitted and their current status.</p>
        </div>
        <Link to="/resident/report" className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">Report a problem</Link>
      </header>

      <Card>
        {loading && <Loading message="Loading your problems..." />}
        {error && (
          <div className="space-y-3">
            <ErrorMessage message={error} />
            <Button variant="secondary" onClick={retry}>Try again</Button>
          </div>
        )}
        {!loading && !error && problems && <ProblemList problems={problems} />}
      </Card>
    </div>
  )
}