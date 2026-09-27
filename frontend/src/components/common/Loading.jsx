export default function Loading({ message = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-600">
      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
      <span>{message}</span>
    </div>
  )
}
