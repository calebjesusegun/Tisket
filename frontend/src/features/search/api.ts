import { request } from '../../lib/api-client'
import type { Page, SearchResult, SearchType } from '../../lib/types'
export const search = (q: string, type: SearchType = 'all') =>
  request<Page<SearchResult>>('/search', { query: { q, type } })
