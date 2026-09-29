import type { Task } from '../../../lib/types'
import { Button } from '../../../components/Button'
import { Badge } from '../../../components/Badge'
import { formatDateTime } from '../../../lib/format'

export function TaskItem({
  task,
  onToggle,
  onEdit,
  onDelete,
  compact = false,
}: {
  task: Task
  onToggle: () => void
  onEdit?: () => void
  onDelete?: () => void
  compact?: boolean
}) {
  return (
    <article
      className={`flex items-start gap-3 rounded-xl border bg-white p-4 ${task.is_overdue ? 'border-red-300 bg-red-50' : 'border-slate-200'}`}
    >
      <input
        aria-label={`Complete ${task.title}`}
        type="checkbox"
        checked={task.status === 'done'}
        onChange={onToggle}
        className="mt-1 size-4 accent-indigo-600"
      />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p
            className={`font-medium ${task.status === 'done' ? 'text-slate-400 line-through' : ''}`}
          >
            {task.title}
          </p>
          <Badge>{task.priority}</Badge>
          {task.is_overdue && <Badge className="bg-red-100 text-red-700">Overdue</Badge>}
        </div>
        {!compact && task.description && (
          <p className="mt-1 text-sm whitespace-pre-wrap text-slate-600">{task.description}</p>
        )}
        {task.due_at && (
          <p className="mt-2 text-xs text-slate-500">Due {formatDateTime(task.due_at)}</p>
        )}
        {task.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {task.tags.map((tag) => (
              <Badge key={tag.id}>#{tag.name}</Badge>
            ))}
          </div>
        )}
      </div>
      {!compact && (
        <div className="flex gap-1">
          <Button size="sm" variant="ghost" onClick={onEdit}>
            Edit
          </Button>
          <Button size="sm" variant="ghost" onClick={onDelete} aria-label={`Delete ${task.title}`}>
            Delete
          </Button>
        </div>
      )}
    </article>
  )
}
