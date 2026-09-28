import AdminDirectoryPage from '../../components/admin/AdminDirectoryPage'

const columns = [
  { key: 'name', label: 'User / resident', render: (record) => record.name || 'Name unavailable' },
  { key: 'email', label: 'Email', render: (record) => record.email || 'Not provided' },
  { key: 'role', label: 'Role', render: (record) => record.role || 'Not provided' },
  { key: 'status', label: 'Status', render: (record) => record.status || 'Status unavailable' },
]

export default function AdminUsersPage() {
  return (
    <AdminDirectoryPage
      resource="users"
      title="Users and residents"
      description="Search user records provided by the admin service."
      searchLabel="Search users and residents"
      searchFields={['name', 'email']}
      filterField="role"
      filterLabel="Filter by role"
      columns={columns}
      caption="Community users and residents"
      detailPath="/admin/users"
    />
  )
}