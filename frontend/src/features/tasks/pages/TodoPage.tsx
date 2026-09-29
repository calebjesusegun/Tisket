import { useState } from 'react'
import { Button } from '../../../components/Button'
import { TextInput } from '../../../components/Field'
import { EmptyState, ErrorState, LoadingState } from '../../../components/States'
import { PageHeader } from '../../../app/PageHeader'
import { useCreateTask, useTasks, useToggleTaskComplete } from '../hooks'
import { TaskItem } from '../components/TaskItem'

export function TodoPage() {
  const [title, setTitle] = useState('')
  const tasks = useTasks({ status: ['todo', 'in_progress'], sort: 'created_at', order: 'desc' })
  const create = useCreateTask()
  const toggle = useToggleTaskComplete()
  return (
    <>
      <PageHeader title="ToDo" description="A quick checklist for what needs doing." />
      <form
        className="mb-5 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          const clean = title.trim()
          if (clean) create.mutate({ title: clean }, { onSuccess: () => setTitle('') })
        }}
      >
        <TextInput
          label="Add a to-do"
          hideLabel
          placeholder="Add a to-do…"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Button type="submit" disabled={!title.trim() || create.isPending}>
          Add
        </Button>
      </form>
      {tasks.isPending ? (
        <LoadingState />
      ) : tasks.isError ? (
        <ErrorState message="Could not load your list." onRetry={() => void tasks.refetch()} />
      ) : tasks.data.items.length ? (
        <div className="flex flex-col gap-2">
          {tasks.data.items.map((task) => (
            <TaskItem key={task.id} task={task} compact onToggle={() => toggle.mutate(task)} />
          ))}
        </div>
      ) : (
        <EmptyState title="All caught up" description="Add a to-do above to get started." />
      )}
    </>
  )
}
