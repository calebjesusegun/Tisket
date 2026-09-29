import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
import type { Task, TaskFilters, TaskInput } from '../../lib/types'

export const taskKeys = {
  all: ['tasks'] as const,
  list: (filters: TaskFilters = {}) => ['tasks', filters] as const,
}
export function useTasks(filters: TaskFilters = {}) {
  return useQuery({ queryKey: taskKeys.list(filters), queryFn: () => api.getTasks(filters) })
}
export function useCreateTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.createTask,
    onSuccess: () => qc.invalidateQueries({ queryKey: taskKeys.all }),
  })
}
export function useUpdateTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: Partial<TaskInput> }) =>
      api.updateTask(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: taskKeys.all }),
  })
}
export function useDeleteTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.deleteTask,
    onSuccess: () => qc.invalidateQueries({ queryKey: taskKeys.all }),
  })
}
export function useToggleTaskComplete() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (task: Task) =>
      api.updateTask(task.id, { status: task.status === 'done' ? 'todo' : 'done' }),
    onMutate: async (task) => {
      await qc.cancelQueries({ queryKey: taskKeys.all })
      const previous = qc.getQueriesData({ queryKey: taskKeys.all })
      qc.setQueriesData({ queryKey: taskKeys.all }, (data: unknown) => {
        const page = data as { items?: Task[] } | undefined
        return page?.items
          ? {
              ...page,
              items: page.items.map((item) =>
                item.id === task.id
                  ? { ...item, status: task.status === 'done' ? 'todo' : 'done' }
                  : item,
              ),
            }
          : data
      })
      return { previous }
    },
    onError: (_error, _task, context) =>
      context?.previous.forEach(([key, data]) => qc.setQueryData(key, data)),
    onSettled: () => qc.invalidateQueries({ queryKey: taskKeys.all }),
  })
}
