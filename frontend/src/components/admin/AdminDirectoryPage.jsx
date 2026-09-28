import { useState } from 'react'
import { Link } from 'react-router-dom'

import AdminDataTable from './AdminDataTable'
import AdminDirectoryFilters from './AdminDirectoryFilters'
import AdminRequestState from './AdminRequestState'
import Card from '../ui/Card'
import useAdminResource from '../../hooks/useAdminResource'

export default function AdminDirectoryPage({
  resource,
  title,
  description,
  searchLabel,
  searchFields,
  filterField,
  filterLabel,
  columns,
  caption,
  detailPath,
}) {
  const { data, loading, error, retry } = useAdminResource(resource)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('')
  const records = Array.isArray(data) ? data : []
  const filterOptions = [...new Set(records.map((record) => record[filterField]).filter((value) => typeof value === 'string' && value.trim()))].sort()
  const normalizedSearch = search.trim().toLowerCase()
  const filteredRecords = records.filter((record) => {
    const matchesSearch = !normalizedSearch || searchFields.some((field) => String(record[field] ?? '').toLowerCase().includes(normalizedSearch))
    const matchesFilter = !filter || String(record[filterField] ?? '') === filter
    return matchesSearch && matchesFilter
  })
  const linkedColumns = columns.map((column, index) => index !== 0 ? column : {
    ...column,
    render: (record) => record.id !== undefined && record.id !== null && String(record.id).trim() !== ''
      ? <Link className="font-semibold text-cyan-800 hover:text-cyan-950" to={`${detailPath}/${encodeURIComponent(record.id)}`}>{column.render(record)}</Link>
      : column.render(record),
  })

  return (
    <div className="space-y-6">
      <header>
        <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/admin">Admin dashboard</Link>
        <h2 className="mt-4 text-3xl font-bold text-slate-950">{title}</h2>
        <p className="mt-2 text-sm text-slate-600">{description}</p>
      </header>

      <AdminRequestState
        loading={loading}
        error={error || (data !== null && !Array.isArray(data) ? 'The admin service returned an unsupported list value.' : '')}
        retry={retry}
        empty={!loading && !error && Array.isArray(data) && data.length === 0}
        emptyTitle={`No ${title.toLowerCase()} available`}
        emptyDescription="Records will appear here when the admin API is available."
      >
        <Card>
          <div className="mb-5">
            <AdminDirectoryFilters
              search={search}
              onSearchChange={setSearch}
              searchLabel={searchLabel}
              filterValue={filter}
              onFilterChange={setFilter}
              filterLabel={filterLabel}
              filterOptions={filterOptions}
            />
          </div>
          <AdminDataTable caption={caption} columns={linkedColumns} rows={filteredRecords} />
        </Card>
      </AdminRequestState>
    </div>
  )
}