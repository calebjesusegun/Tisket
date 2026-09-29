import { PageHeader } from '../../../app/PageHeader'
import { EmptyState, ErrorState, LoadingState } from '../../../components/States'
import { useDueSoon, useOverdue } from '../hooks'
import { TaskItem } from '../../tasks/components/TaskItem'
import { useToggleTaskComplete } from '../../tasks/hooks'

export function DueSoonPage() {
  const due = useDueSoon()
  const overdue = useOverdue()
  const toggle = useToggleTaskComplete()
  const loading = due.isPending || overdue.isPending
  const error = due.isError || overdue.isError
  return (
    <>
      <PageHeader
        title="Due soon"
        description="Overdue tasks and tasks due in the next 48 hours."
      />
      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState
          message="Could not load reminders."
          onRetry={() => {
            void due.refetch()
            void overdue.refetch()
          }}
        />
      ) : (
        <div className="space-y-7">
          {[
            ['Overdue', overdue.data?.items ?? []],
            ['Next 48 hours', due.data?.items ?? []],
          ].map(([title, rows]) => (
            <section key={title as string}>
              <h2 className="mb-3 text-lg font-semibold">{title as string}</h2>
              {(rows as NonNullable<typeof overdue.data>['items']).length ? (
                <div className="space-y-2">
                  {(rows as NonNullable<typeof overdue.data>['items']).map((task) => (
                    <TaskItem
                      key={task.id}
                      task={task}
                      compact
                      onToggle={() => toggle.mutate(task)}
                    />
                  ))}
                </div>
              ) : (
                <EmptyState title={`No ${String(title).toLowerCase()} tasks`} />
              )}
            </section>
          ))}
        </div>
      )}
    </>
  )
}
