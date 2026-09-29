import { QueryClient } from '@tanstack/react-query'
import { ApiError } from './api-client'

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        refetchOnWindowFocus: true,
        // Don't retry client errors (4xx); retry once for network/server errors.
        retry: (failureCount, error) =>
          !(error instanceof ApiError && error.status >= 400 && error.status < 500) &&
          failureCount < 1,
      },
      mutations: { retry: false },
    },
  })
}
