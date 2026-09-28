export default function PriorityBadge({ priority }) {
  const label = typeof priority === 'string' && priority.trim() ? priority.trim() : 'Priority unavailable'

  return (
    <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 ring-1 ring-inset ring-slate-200">
      {label}
    </span>
  )
}