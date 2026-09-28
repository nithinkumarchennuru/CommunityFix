import EmptyState from '../common/EmptyState'
import ErrorMessage from '../common/ErrorMessage'
import Loading from '../common/Loading'
import Button from '../ui/Button'

export default function AdminRequestState({ loading, error, retry, empty, emptyTitle, emptyDescription, children }) {
  if (loading) return <Loading message="Loading admin data..." />

  if (error) {
    return (
      <div className="space-y-3">
        <ErrorMessage message={error} />
        {retry && <Button variant="secondary" onClick={retry}>Try again</Button>}
      </div>
    )
  }

  if (empty) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />
  }

  return children
}