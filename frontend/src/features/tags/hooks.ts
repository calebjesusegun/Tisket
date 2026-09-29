import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
export const useTags = () => useQuery({ queryKey: ['tags'], queryFn: api.getTags })
export function useRenameTag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => api.renameTag(id, name),
    onSuccess: () => {
      void qc.invalidateQueries()
    },
  })
}
export function useDeleteTag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.deleteTag,
    onSuccess: () => {
      void qc.invalidateQueries()
    },
  })
}
