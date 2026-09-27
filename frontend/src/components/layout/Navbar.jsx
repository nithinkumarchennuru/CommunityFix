import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'

const navItems = [
  { label: 'Resident', to: '/resident', role: 'resident' },
  { label: 'Worker', to: '/worker', role: 'worker' },
  { label: 'Admin', to: '/admin', role: 'admin' },
]

export default function Navbar() {
  const { isAuthenticated, role, logout } = useAuth()
  const visibleNavItems = navItems.filter((item) => item.role === role)

  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-600">CommunityFix</p>
          <h1 className="text-lg font-bold text-slate-900">Operations Console</h1>
        </div>

        <nav aria-label="Account navigation" className="hidden items-center gap-2 md:flex">
          {isAuthenticated && visibleNavItems.map(({ label, to }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                [
                  'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-cyan-50 text-cyan-700 ring-1 ring-cyan-200'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                ].join(' ')
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        {isAuthenticated ? (
          <button
            type="button"
            onClick={logout}
            className="rounded-lg border border-slate-200 bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700"
          >
            Sign out
          </button>
        ) : (
          <NavLink
            to="/login"
            className="rounded-lg border border-slate-200 bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-700"
          >
            Sign in
          </NavLink>
        )}
      </div>
    </header>
  )
}
