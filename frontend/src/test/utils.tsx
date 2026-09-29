import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, type RenderOptions } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'
import { createMemoryRouter, type RouteObject } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { ToastProvider } from '../components/Toast'
import { routes as appRoutes } from '../app/routes'

export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: 0 }, mutations: { retry: false } },
  })
}

export function Providers({
  children,
  queryClient = createTestQueryClient(),
}: {
  children: ReactNode
  queryClient?: QueryClient
}) {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider duration={60_000}>{children}</ToastProvider>
    </QueryClientProvider>
  )
}

interface RenderRouteOptions {
  route?: string
  routes?: RouteObject[]
  queryClient?: QueryClient
}

/** Render the real app routes (or custom ones) at a given URL with all providers. */
export function renderRoute({
  route = '/',
  routes = appRoutes,
  queryClient = createTestQueryClient(),
}: RenderRouteOptions = {}) {
  const router = createMemoryRouter(routes, { initialEntries: [route] })
  const utils = render(
    <Providers queryClient={queryClient}>
      <RouterProvider router={router} />
    </Providers>,
  )
  return { ...utils, router, queryClient }
}

/** Render a single element with providers inside a minimal router. */
export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    queryClient = createTestQueryClient(),
    ...options
  }: RenderRouteOptions & Omit<RenderOptions, 'wrapper'> = {},
) {
  const router = createMemoryRouter([{ path: '*', element: ui }], { initialEntries: [route] })
  const utils = render(
    <Providers queryClient={queryClient}>
      <RouterProvider router={router} />
    </Providers>,
    options,
  )
  return { ...utils, router, queryClient }
}
