import { request } from '../../lib/api-client'
import type { Page, Task } from '../../lib/types'
export const getDueSoon = () => request<Page<Task>>('/reminders/due-soon')
export const getOverdue = () => request<Page<Task>>('/reminders/overdue')
export const getNotifications = () => request<Page<Task>>('/reminders/notifications')
export const dismissNotification = (id: number) =>
  request<Task>(`/reminders/${id}/dismiss`, { method: 'POST' })
export const dismissAll = () =>
  request<{ dismissed: number }>('/reminders/dismiss-all', { method: 'POST' })
