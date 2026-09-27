import { Link } from 'react-router-dom'

import EmptyState from '../../components/common/EmptyState'
import ErrorMessage from '../../components/common/ErrorMessage'
import Loading from '../../components/common/Loading'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import ProblemList from '../../components/resident/ProblemList'
import useResidentResource from '../../hooks/useResidentResource'

export default function ResidentPage() {
  const { data: problems, loading, error, retry } = useResidentResource('problems')
  const categoriesCount = problems
    ? new Set(problems.map((problem) => problem.category).filter(Boolean)).size
    : '—'
  const photoCount = problems
    ? problems.filter((problem) => problem.photoUrl).length
    : '—'

  return (
    <div className="space-y-8">
      <section className="flex flex-col justify-between gap-5 border-b border-slate-200 pb-7 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">Resident home</p>
          <h2 className="mt-2 text-3xl font-bold text-slate-950">Your neighborhood, made better.</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">Report a local issue and keep track of its progress in one place.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link to="/resident/report" className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">Report a problem</Link>
          <Link to="/resident/problems" className="inline-flex items-center justify-center rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition-colors hover:bg-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">View my problems</Link>
        </div>
      </section>

      <section aria-label="Problem summary" className="grid gap-4 sm:grid-cols-3">
        {[
          { label: 'Total reports', value: problems?.length ?? '—', detail: 'Reported by you' },
          { label: 'Categories', value: categoriesCount, detail: 'Across your reports' },
          { label: 'Photos', value: photoCount, detail: 'Attached to reports' },
        ].map(({ label, value, detail }) => (
          <Card key={label} className="border-t-4 border-t-cyan-700">
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className="mt-3 text-3xl font-bold text-slate-950">{value}</p>
            <p className="mt-1 text-xs text-slate-500">{detail}</p>
          </Card>
        ))}
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-semibold text-slate-950">Recent problems</h3>
            <p className="mt-1 text-sm text-slate-600">Your latest community reports.</p>
          </div>
          <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/resident/problems">All problems</Link>
        </div>

        {loading && <Loading message="Loading your problems..." />}
        {error && (
          <div className="space-y-3">
            <ErrorMessage message={error} />
            <Button variant="secondary" onClick={retry}>Try again</Button>
          </div>
        )}
        {!loading && !error && problems?.length === 0 && (
          <EmptyState title="A clear start" description="You have not reported a community problem yet. Use Report a problem to get started." />
        )}
        {!loading && !error && problems?.length > 0 && <ProblemList problems={problems.slice(0, 3)} />}
      </section>
    </div>
  )
}
