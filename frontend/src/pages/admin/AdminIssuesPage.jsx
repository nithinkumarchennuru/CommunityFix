import AdminDirectoryPage from '../../components/admin/AdminDirectoryPage'

const columns = [
  { key: 'title', label: 'Issue / job', render: (record) => record.title || 'Title unavailable' },
  { key: 'category', label: 'Category', render: (record) => record.category || 'Not provided' },
  { key: 'priority', label: 'Priority', render: (record) => record.priority || 'Not provided' },
  { key: 'status', label: 'Status', render: (record) => record.status || 'Status unavailable' },
]

export default function AdminIssuesPage() {
  return (
    <AdminDirectoryPage
      resource="issues"
      title="Issues and jobs"
      description="Search and review reported community issues and related jobs."
      searchLabel="Search issues and jobs"
      searchFields={['title', 'description', 'category', 'location']}
      filterField="status"
      filterLabel="Filter by status"
      columns={columns}
      caption="Community issues and jobs"
      detailPath="/admin/issues"
    />
  )
}