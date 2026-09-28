import Input from '../ui/Input'

export default function AdminDirectoryFilters({
  search,
  onSearchChange,
  searchLabel,
  filterValue,
  onFilterChange,
  filterLabel,
  filterOptions,
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Input
        id="admin-search"
        label={searchLabel}
        type="search"
        value={search}
        onChange={(event) => onSearchChange(event.target.value)}
        placeholder="Search records"
      />
      <div className="space-y-2">
        <label htmlFor="admin-filter" className="block text-sm font-medium text-slate-700">{filterLabel}</label>
        <select
          id="admin-filter"
          value={filterValue}
          onChange={(event) => onFilterChange(event.target.value)}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
        >
          <option value="">All</option>
          {filterOptions.map((option) => <option key={option} value={option}>{option}</option>)}
        </select>
      </div>
    </div>
  )
}