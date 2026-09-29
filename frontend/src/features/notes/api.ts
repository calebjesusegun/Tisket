import { request } from '../../lib/api-client'
import type { Note, NoteFilters, NoteInput, Page } from '../../lib/types'
export function getNotes(filters: NoteFilters = {}) {
  return request<Page<Note>>('/notes', {
    query: filters as Record<string, string | number | boolean | undefined>,
  })
}
export const getNote = (id: number) => request<Note>(`/notes/${id}`)
export const saveNote = (input: NoteInput, id?: number) =>
  request<Note>(id ? `/notes/${id}` : '/notes', { method: id ? 'PATCH' : 'POST', body: input })
export const deleteNote = (id: number) => request<void>(`/notes/${id}`, { method: 'DELETE' })
