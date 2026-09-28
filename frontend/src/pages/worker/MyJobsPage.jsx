import { Link } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import Loading from '../../components/common/Loading'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import JobList from '../../components/worker/JobList'
import useWorkerResource from '../../hooks/useWorkerResource'

export default function MyJobsPage() {
  const { data: jobs, loading, error, retry } = useWorkerResource('jobs')

  return (
    <div className="space-y-6">
      <header>
        <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/worker">Worker dashboard</Link>
        <h2 className="mt-4 text-3xl font-bold text-slate-950">My jobs</h2>
        <p className="mt-2 text-sm text-slate-600">Jobs assigned to your account, as supplied by the worker service.</p>
      </header>
      <Card>
        {loading && <Loading message="Loading assigned jobs..." />}
        {error && (
          <div className="space-y-3">
            <ErrorMessage message={error} />
            <Button variant="secondary" onClick={retry}>Try again</Button>
          </div>
        )}
        {!loading && !error && jobs && <JobList jobs={jobs} />}
      </Card>
    </div>
  )
}