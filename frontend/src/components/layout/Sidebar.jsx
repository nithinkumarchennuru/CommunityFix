import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'

const navigation = [
  { label: 'Overview', to: '/resident', role: 'resident' },
  { label: 'Worker View', to: '/worker', role: 'worker' },
  { label: 'Admin View', to: '/admin', role: 'admin' },
]

export default function Sidebar() {
  const { role } = useAuth()
  const visibleNavigation = navigation.filter((item) => item.role === role)

  return (
    <aside className="hidden w-64 shrink-0 rounded-2xl bg-slate-900 p-4 text-slate-200 lg:block">
      <p className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Navigation</p>

      <nav className="space-y-2">
        {visibleNavigation.map(({ label, to }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [
                'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-slate-800 text-white ring-1 ring-slate-700'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white',
              ].join(' ')
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
