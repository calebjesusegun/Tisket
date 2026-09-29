import { useQuery } from '@tanstack/react-query'
import { search } from './api'
import type { SearchType } from '../../lib/types'
export const useSearch = (q: string, type: SearchType = 'all') =>
  useQuery({
    queryKey: ['search', q, type],
    queryFn: () => search(q, type),
    enabled: Boolean(q.trim()),
  })
