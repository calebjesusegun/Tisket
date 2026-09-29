import { useState } from 'react'
import { Button } from '../../../components/Button'
import { Modal } from '../../../components/Modal'
import { EmptyState, ErrorState, LoadingState } from '../../../components/States'
import { SelectInput } from '../../../components/Field'
import {
  useCreateTask,
  useDeleteTask,
  useTasks,
  useToggleTaskComplete,
  useUpdateTask,
} from '../hooks'
import { TaskItem } from '../components/TaskItem'
import { TaskForm } from '../components/TaskForm'
import { PageHeader } from '../../../app/PageHeader'
import type { Task, TaskFilters } from '../../../lib/types'
import { useTags } from '../../tags/hooks'

export function TasksPage() {
  const [filters, setFilters] = useState<TaskFilters>({ sort: 'created_at', order: 'desc' })
  const [editing, setEditing] = useState<Task | null | undefined>(undefined)
  const tasks = useTasks(filters)
  const tags = useTags()
  const create = useCreateTask()
  const update = useUpdateTask()
  const remove = useDeleteTask()
  const toggle = useToggleTaskComplete()
  return (
    <>
      <PageHeader
        title="Tasks"
        description="Plan and manage work in your shared workspace."
        actions={<Button onClick={() => setEditing(null)}>New task</Button>}
      />
      <div className="mb-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        <SelectInput
          label="Status"
          value={filters.status?.[0] ?? ''}
          onChange={(e) =>
            setFilters({
              ...filters,
              status: e.target.value ? [e.target.value as 'todo'] : undefined,
            })
          }
        >
          <option value="">Any status</option>
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </SelectInput>
        <SelectInput
          label="Priority"
          value={filters.priority ?? ''}
          onChange={(e) =>
            setFilters({
              ...filters,
              priority: e.target.value ? (e.target.value as TaskFilters['priority']) : undefined,
            })
          }
        >
          <option value="">Any priority</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </SelectInput>
        <SelectInput
          label="Tag"
          value={filters.tag ?? ''}
          onChange={(e) => setFilters({ ...filters, tag: e.target.value || undefined })}
        >
          <option value="">Any tag</option>
          {tags.data?.map((tag) => (
            <option key={tag.id} value={tag.name}>
              {tag.name}
            </option>
          ))}
        </SelectInput>
        <SelectInput
          label="Sort"
          value={filters.sort}
          onChange={(e) => setFilters({ ...filters, sort: e.target.value as TaskFilters['sort'] })}
        >
          <option value="created_at">Recently added</option>
          <option value="due_at">Due date</option>
          <option value="priority">Priority</option>
          <option value="title">Title</option>
        </SelectInput>
      </div>
      {tasks.isPending ? (
        <LoadingState />
      ) : tasks.isError ? (
        <ErrorState message="Could not load tasks." onRetry={() => void tasks.refetch()} />
      ) : tasks.data.items.length === 0 ? (
        <EmptyState title="No tasks yet" description="Create a task or adjust your filters." />
      ) : (
        <div className="flex flex-col gap-2">
          {tasks.data.items.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={() => toggle.mutate(task)}
              onEdit={() => setEditing(task)}
              onDelete={() => remove.mutate(task.id)}
            />
          ))}
        </div>
      )}
      <Modal
        open={editing !== undefined}
        title={editing ? 'Edit task' : 'New task'}
        onClose={() => setEditing(undefined)}
      >
        {editing !== undefined && (
          <TaskForm
            task={editing ?? undefined}
            busy={create.isPending || update.isPending}
            onSubmit={(input) =>
              editing
                ? update.mutate(
                    { id: editing.id, input },
                    { onSuccess: () => setEditing(undefined) },
                  )
                : create.mutate(input, { onSuccess: () => setEditing(undefined) })
            }
          />
        )}
      </Modal>
    </>
  )
}
