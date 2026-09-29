import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
export const useDueSoon = () =>
  useQuery({ queryKey: ['reminders', 'due-soon'], queryFn: api.getDueSoon })
export const useOverdue = () =>
  useQuery({ queryKey: ['reminders', 'overdue'], queryFn: api.getOverdue })
export const useNotifications = () =>
  useQuery({
    queryKey: ['reminders', 'notifications'],
    queryFn: api.getNotifications,
    refetchInterval: 60_000,
  })
export function useDismissNotification() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.dismissNotification,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }),
  })
}
export function useDismissAll() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.dismissAll,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }),
  })
}
