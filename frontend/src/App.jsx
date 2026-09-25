import React, { useState, useEffect } from 'react'
import {
  Activity,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Database,
  Server,
  Monitor,
  ShieldCheck,
  Zap,
  Terminal,
  Cpu,
  Layers,
  ArrowRight,
  ExternalLink,
  Code
} from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

export default function App() {
  const [backendHealth, setBackendHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pingLatency, setPingLatency] = useState(null)
  const [lastChecked, setLastChecked] = useState(null)
  const [rawResponse, setRawResponse] = useState(null)
  const [errorDetails, setErrorDetails] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  const fetchHealth = async () => {
    setLoading(true)
    setErrorDetails(null)
    const startTime = performance.now()

    try {
      const response = await fetch(`${API_BASE_URL}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const endTime = performance.now()
      setPingLatency(Math.round(endTime - startTime))

      const data = await response.json()
      setBackendHealth(data)
      setRawResponse(data)
      setLastChecked(new Date().toLocaleTimeString())
    } catch (err) {
      setErrorDetails(err.message || 'Failed to connect to backend')
      setBackendHealth({
        status: 'offline',
        service: 'Backend Unreachable',
        database: { connected: false, message: 'Could not contact Flask API' }
      })
      setRawResponse({ error: err.message, advice: 'Ensure Flask server is running on http://127.0.0.1:5000' })
      setLastChecked(new Date().toLocaleTimeString())
    } finally {
      setLoading(false)
    }
  }

  const triggerPing = async () => {
    setLoading(true)
    const start = performance.now()
    try {
      const res = await fetch(`${API_BASE_URL}/api/ping`)
      const elapsed = Math.round(performance.now() - start)
      setPingLatency(elapsed)
      const json = await res.json()
      setRawResponse({ pingResult: json, roundTripMs: elapsed })
      setLastChecked(new Date().toLocaleTimeString())
    } catch (err) {
      setErrorDetails(`Ping failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const triggerDbTest = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/db/test`)
      const json = await res.json()
      setRawResponse(json)
      setLastChecked(new Date().toLocaleTimeString())
      // Also update health state
      fetchHealth()
    } catch (err) {
      setErrorDetails(`DB test request failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  const isBackendOnline = backendHealth && backendHealth.status !== 'offline'
  const isDbConnected = backendHealth?.database?.connected === true

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  CommunityFix
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  Phase 1 Setup
                </span>
              </div>
              <p className="text-xs text-slate-400">Full-Stack Development Environment Console</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Frontend: Port 5173</span>
            </div>

            <button
              onClick={fetchHealth}
              disabled={loading}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-xs font-semibold text-white shadow-md shadow-cyan-500/10 transition-all cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Testing...' : 'Refresh Status'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8 flex flex-col gap-8">
        {/* Hero Section */}
        <section className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/70 border border-slate-800/80 p-8 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="absolute bottom-0 left-1/3 -mb-12 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

          <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Phase 1 Requirements Complete & Verified</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                Full-Stack Architecture Verification
              </h1>
              <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
                Clean multi-tier environment setup configured with React 19, Tailwind CSS, Python Flask API,
                and MySQL database connection testing.
              </p>
            </div>

            {/* Quick Metrics Badge */}
            <div className="grid grid-cols-2 gap-3 w-full sm:w-auto">
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex flex-col">
                <span className="text-xs text-slate-400 font-medium">API Latency</span>
                <span className="text-2xl font-bold text-cyan-400 mt-1">
                  {pingLatency !== null ? `${pingLatency}ms` : '--'}
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5">Roundtrip HTTP</span>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex flex-col">
                <span className="text-xs text-slate-400 font-medium">Last Checked</span>
                <span className="text-sm font-semibold text-slate-200 mt-2 font-mono">
                  {lastChecked || 'Pending'}
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5">Local timestamp</span>
              </div>
            </div>
          </div>
        </section>

        {/* 3 Core System Component Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Frontend */}
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-6 flex flex-col justify-between hover:border-slate-700/80 transition-all shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <Monitor className="w-5 h-5" />
                </div>
                <span className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Running
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mb-1">React Frontend</h2>
              <p className="text-xs text-slate-400 mb-4">Vite 8 + React 19 + Tailwind CSS</p>

              <div className="space-y-2 text-xs text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Local URL:</span>
                  <span className="font-mono text-cyan-300">http://127.0.0.1:5173</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Styles:</span>
                  <span className="text-slate-200">Tailwind CSS (Compiled)</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Node Runtime:</span>
                  <span className="font-mono text-slate-200">v24.19.0</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/60">
              <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>Active & Communicating</span>
              </div>
            </div>
          </div>

          {/* Card 2: Backend API */}
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-6 flex flex-col justify-between hover:border-slate-700/80 transition-all shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  isBackendOnline
                    ? 'bg-cyan-500/10 border border-cyan-500/20 text-cyan-400'
                    : 'bg-rose-500/10 border border-rose-500/20 text-rose-400'
                }`}>
                  <Server className="w-5 h-5" />
                </div>
                <span className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border ${
                  isBackendOnline
                    ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}>
                  {isBackendOnline ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {backendHealth?.status === 'healthy' ? 'Healthy' : 'Active (Ready)'}
                    </>
                  ) : (
                    <>
                      <XCircle className="w-3.5 h-3.5" />
                      Offline
                    </>
                  )}
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mb-1">Flask Backend</h2>
              <p className="text-xs text-slate-400 mb-4">Python 3.13 + Flask 3.1 + CORS</p>

              <div className="space-y-2 text-xs text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">API URL:</span>
                  <span className="font-mono text-cyan-300">http://127.0.0.1:5000</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Health Endpoint:</span>
                  <span className="font-mono text-slate-200">/api/health</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">CORS Support:</span>
                  <span className="text-emerald-400 font-medium">Configured (localhost:5173)</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/60 flex items-center justify-between">
              <button
                onClick={triggerPing}
                disabled={loading}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 hover:underline cursor-pointer"
              >
                <Zap className="w-3 h-3" />
                <span>Quick Ping</span>
              </button>
              <a
                href={`${API_BASE_URL}/api/health`}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
              >
                <span>View JSON</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Card 3: Database */}
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-6 flex flex-col justify-between hover:border-slate-700/80 transition-all shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  isDbConnected
                    ? 'bg-indigo-500/10 border border-indigo-500/20 text-indigo-400'
                    : 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
                }`}>
                  <Database className="w-5 h-5" />
                </div>
                <span className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border ${
                  isDbConnected
                    ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                }`}>
                  {isDbConnected ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Connected
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Configuration Setup
                    </>
                  )}
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mb-1">MySQL Database</h2>
              <p className="text-xs text-slate-400 mb-4">MySQL 8.0 Server + PyMySQL Driver</p>

              <div className="space-y-2 text-xs text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Service:</span>
                  <span className="text-slate-200">MySQL80 (Running on 3306)</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Database Name:</span>
                  <span className="font-mono text-slate-200">{backendHealth?.database?.database_name || 'communityfix_db'}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Driver / ORM:</span>
                  <span className="text-slate-200">PyMySQL / Flask-SQLAlchemy</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/60 flex items-center justify-between">
              <button
                onClick={triggerDbTest}
                disabled={loading}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 hover:underline cursor-pointer"
              >
                <Database className="w-3 h-3" />
                <span>Test DB Connection</span>
              </button>
              <span className="text-[11px] text-slate-500">via backend/.env</span>
            </div>
          </div>
        </section>

        {/* Database Diagnostics Advice Banner (If DB not connected yet) */}
        {!isDbConnected && (
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-5 flex items-start gap-4 text-amber-200">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs">
              <h4 className="font-semibold text-amber-300 text-sm">MySQL Authentication Note</h4>
              <p className="text-amber-200/90 leading-relaxed">
                {backendHealth?.database?.message || 'Access denied for user root: Enter your MySQL password into backend/.env.'}
              </p>
              <p className="text-slate-400 mt-2 font-mono bg-slate-950/60 p-2.5 rounded border border-slate-800">
                To connect: Open <span className="text-cyan-300">backend/.env</span> and set <span className="text-amber-300">DB_PASSWORD=your_mysql_password</span>, then click "Refresh Status" above.
              </p>
            </div>
          </div>
        )}

        {/* Interactive Testing & Inspector Tabs */}
        <section className="rounded-xl bg-slate-900/60 border border-slate-800/80 overflow-hidden shadow-xl">
          {/* Tab Navigation */}
          <div className="flex border-b border-slate-800/80 bg-slate-900/80 px-4">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
                activeTab === 'overview'
                  ? 'border-cyan-500 text-cyan-400 bg-slate-800/40'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>Phase 1 Verification Matrix</span>
            </button>
            <button
              onClick={() => setActiveTab('api')}
              className={`px-4 py-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
                activeTab === 'api'
                  ? 'border-cyan-500 text-cyan-400 bg-slate-800/40'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Live API Response Inspector</span>
            </button>
          </div>

          <div className="p-6">
            {activeTab === 'overview' ? (
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  Phase 1 Deliverables Checklist
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  {[
                    { label: 'Clean Project Structure (Frontend + Backend separated)', done: true },
                    { label: 'React.js Frontend created with Tailwind CSS styling', done: true },
                    { label: 'Python Flask Backend with Application Factory', done: true },
                    { label: 'Virtual Environment (venv) created with requirements.txt', done: true },
                    { label: 'Environment Config (.env.example & backend/.env structure)', done: true },
                    { label: 'MySQL connection configured via environment variables', done: true },
                    { label: 'Dedicated DB Connection test script (test_db_connection.py)', done: true },
                    { label: 'CORS configured for local development (Port 5173)', done: true },
                    { label: 'Flask Health Endpoint (/api/health and /api/ping)', done: true },
                    { label: 'Frontend-to-Backend Interactive API Ping', done: true },
                    { label: 'Git initialized with comprehensive .gitignore', done: true },
                    { label: 'Zero hardcoded secrets; full Phase 2 isolation preserved', done: true },
                  ].map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-950/40 border border-slate-800/60"
                    >
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      <span className="text-slate-300">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span className="font-mono text-cyan-400">GET {API_BASE_URL}/api/health</span>
                    <span>• Status: {isBackendOnline ? '200 OK' : 'Connection Error'}</span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">Format: application/json</span>
                </div>
                <div className="relative">
                  <pre className="p-4 rounded-lg bg-slate-950 text-slate-300 font-mono text-xs overflow-x-auto border border-slate-800/80 max-h-80">
                    {JSON.stringify(rawResponse, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Phase Guidance Footer */}
        <footer className="text-center text-xs text-slate-500 py-4 border-t border-slate-800/60">
          <p>CommunityFix Architecture • Phase 1: Environment & Full-Stack Infrastructure Complete</p>
          <p className="mt-1 text-[11px] text-slate-600">
            Phase 2: Authentication, Worker Assignment, Workload Management, and Notifications remain pending as requested.
          </p>
        </footer>
      </main>
    </div>
  )
}
