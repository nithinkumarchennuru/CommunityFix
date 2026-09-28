import AdminDirectoryPage from '../../components/admin/AdminDirectoryPage'
import WorkerStatusBadge from '../../components/worker/WorkerStatusBadge'

const columns = [
  { key: 'name', label: 'Worker', render: (record) => record.name || 'Name unavailable' },
  { key: 'email', label: 'Email', render: (record) => record.email || 'Not provided' },
  { key: 'availability', label: 'Availability', render: (record) => <WorkerStatusBadge status={record.availability} /> },
]

export default function AdminWorkersPage() {
  return (
    <AdminDirectoryPage
      resource="workers"
      title="Workers"
      description="Search the worker records provided by the admin service."
      searchLabel="Search workers"
      searchFields={['name', 'email']}
      filterField="availability"
      filterLabel="Filter by availability"
      columns={columns}
      caption="Community workers"
      detailPath="/admin/workers"
    />
  )
}