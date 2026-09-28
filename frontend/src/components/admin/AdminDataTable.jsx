export default function AdminDataTable({ caption, columns, rows, emptyMessage = 'No matching records.' }) {
  if (rows.length === 0) {
    return <p className="py-8 text-center text-sm text-slate-600">{emptyMessage}</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse text-left text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            {columns.map((column) => <th key={column.key} scope="col" className="px-3 py-3 font-semibold">{column.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id ?? index} className="border-b border-slate-100 last:border-0">
              {columns.map((column) => <td key={column.key} className="px-3 py-4 text-slate-700">{column.render(row)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}