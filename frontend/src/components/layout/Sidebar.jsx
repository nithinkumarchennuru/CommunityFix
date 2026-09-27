import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'

const navigation = [
  { label: 'Dashboard', to: '/resident', role: 'resident' },
  { label: 'Report problem', to: '/resident/report', role: 'resident' },
  { label: 'My problems', to: '/resident/problems', role: 'resident' },
  { label: 'Worker View', to: '/worker', role: 'worker' },
  { label: 'Admin View', to: '/admin', role: 'admin' },
]

export default function Sidebar() {
  const { role } = useAuth()
  const navigationRole = role || 'resident'
  const visibleNavigation = navigation.filter((item) => item.role === navigationRole)

  return (
    <aside className="w-full shrink-0 rounded-xl bg-slate-900 p-3 text-slate-200 lg:w-64 lg:rounded-2xl lg:p-4">
      <p className="mb-3 px-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Navigation</p>

      <nav aria-label="Main navigation" className="flex gap-1 overflow-x-auto lg:flex-col lg:gap-2">
        {visibleNavigation.map(({ label, to }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/resident'}
            className={({ isActive }) =>
              [
                'flex shrink-0 items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors',
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
