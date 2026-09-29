import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
import type { NoteFilters, NoteInput } from '../../lib/types'
export const useNotes = (filters: NoteFilters = {}) =>
  useQuery({ queryKey: ['notes', filters], queryFn: () => api.getNotes(filters) })
export const useNote = (id: number) =>
  useQuery({
    queryKey: ['notes', id],
    queryFn: () => api.getNote(id),
    enabled: Number.isFinite(id),
  })
export function useSaveNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ input, id }: { input: NoteInput; id?: number }) => api.saveNote(input, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  })
}
export function useDeleteNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.deleteNote,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  })
}
