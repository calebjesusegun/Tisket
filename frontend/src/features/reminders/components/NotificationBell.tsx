import { useEffect, useMemo, useRef, useState } from 'react'
import { Button } from '../../../components/Button'
import { useToast } from '../../../components/toast-context'
import { useDismissAll, useDismissNotification, useNotifications } from '../hooks'

const EMPTY_TASKS: NonNullable<ReturnType<typeof useNotifications>['data']>['items'] = []

export function NotificationBell() {
  const notifications = useNotifications()
  const dismiss = useDismissNotification()
  const dismissAll = useDismissAll()
  const [open, setOpen] = useState(false)
  const { notify } = useToast()
  const prior = useRef<number[] | null>(null)
  const tasks = notifications.data?.items ?? EMPTY_TASKS
  const taskIds = useMemo(() => tasks.map((task) => task.id), [tasks])
  useEffect(() => {
    if (prior.current && taskIds.some((id) => !prior.current?.includes(id)))
      notify('A task is due now.', 'warning')
    prior.current = taskIds
  }, [taskIds, notify])
  return (
    <div className="relative">
      <Button
        variant="ghost"
        aria-label={`Notifications${tasks.length ? `, ${tasks.length} due` : ''}`}
        onClick={() => setOpen(!open)}
      >
        <span aria-hidden="true">♢</span>
        {tasks.length > 0 && (
          <span className="ml-1 rounded-full bg-red-600 px-1.5 text-xs text-white">
            {tasks.length}
          </span>
        )}
      </Button>
      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 max-w-[90vw] rounded-xl border border-slate-200 bg-white p-3 shadow-xl">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="font-semibold">Due tasks</h2>
            {tasks.length > 0 && (
              <Button size="sm" variant="ghost" onClick={() => dismissAll.mutate()}>
                Dismiss all
              </Button>
            )}
          </div>
          {tasks.length ? (
            <ul className="space-y-2">
              {tasks.map((task) => (
                <li key={task.id} className="flex items-center justify-between gap-2 text-sm">
                  <span>{task.title}</span>
                  <Button size="sm" variant="secondary" onClick={() => dismiss.mutate(task.id)}>
                    Dismiss
                  </Button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No due task notifications.</p>
          )}
        </div>
      )}
    </div>
  )
}
