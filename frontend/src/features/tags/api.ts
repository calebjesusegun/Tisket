import { request } from '../../lib/api-client'
import type { Tag, TagWithCounts } from '../../lib/types'
export const getTags = () => request<TagWithCounts[]>('/tags')
export const renameTag = (id: number, name: string) =>
  request<Tag>(`/tags/${id}`, { method: 'PATCH', body: { name } })
export const deleteTag = (id: number) => request<void>(`/tags/${id}`, { method: 'DELETE' })
