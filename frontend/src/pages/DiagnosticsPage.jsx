import { useState } from 'react'

import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Loading from '../components/common/Loading'
import ErrorMessage from '../components/common/ErrorMessage'
import { getHealth, pingApi, testDatabaseConnection } from '../services/healthService'

const initialDiagnosticsState = {
  health: null,
  ping: null,
  db: null,
}

export default function DiagnosticsPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState(initialDiagnosticsState)

  const runDiagnostics = async () => {
    setLoading(true)
    setError('')

    try {
      const [healthResult, pingResult, dbResult] = await Promise.all([
        getHealth(),
        pingApi(),
        testDatabaseConnection(),
      ])

      setResults({
        health: healthResult,
        ping: pingResult,
        db: dbResult,
      })
    } catch (err) {
      setError(err.message || 'Unable to reach the backend services.')
      setResults(initialDiagnosticsState)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-600">Diagnostics</p>
          <h2 className="mt-2 text-3xl font-bold text-slate-900">Frontend connectivity check</h2>
        </div>

        <Button onClick={runDiagnostics} variant="secondary">
          Refresh
        </Button>
      </div>

      {loading && <Loading message="Checking frontend to backend connectivity..." />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card title="Health" subtitle="GET /api/health">
            <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-slate-700">
              {JSON.stringify(results.health, null, 2)}
            </pre>
          </Card>

          <Card title="Ping" subtitle="GET /api/ping">
            <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-slate-700">
              {JSON.stringify(results.ping, null, 2)}
            </pre>
          </Card>

          <Card title="Database" subtitle="GET /api/db/test">
            <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-slate-700">
              {JSON.stringify(results.db, null, 2)}
            </pre>
          </Card>
        </div>
      )}
    </div>
  )
}
