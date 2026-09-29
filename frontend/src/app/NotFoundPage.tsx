import { Link } from 'react-router'
import { EmptyState } from '../components/States'

export function NotFoundPage() {
  return (
    <EmptyState
      title="Page not found"
      description="The page you are looking for does not exist."
      action={
        <Link to="/todo" className="text-sm font-medium text-indigo-600 hover:underline">
          Back to your ToDo list
        </Link>
      }
    />
  )
}
