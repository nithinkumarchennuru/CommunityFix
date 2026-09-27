export default function ErrorMessage({ message }) {
  return (
    <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
      {message || 'Something went wrong.'}
    </div>
  )
}
