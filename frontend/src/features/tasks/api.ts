import { request } from '../../lib/api-client'
import type { Page, Task, TaskFilters, TaskInput } from '../../lib/types'

export function getTasks(filters: TaskFilters = {}) {
  return request<Page<Task>>('/tasks', {
    query: filters as Record<string, string | number | boolean | undefined>,
  })
}
export function createTask(input: TaskInput) {
  return request<Task>('/tasks', { method: 'POST', body: input })
}
export function updateTask(id: number, input: Partial<TaskInput>) {
  return request<Task>(`/tasks/${id}`, { method: 'PATCH', body: input })
}
export function deleteTask(id: number) {
  return request<void>(`/tasks/${id}`, { method: 'DELETE' })
}
