import { QueryClient } from '@tanstack/react-query'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'
import { useToggleTaskComplete, taskKeys } from './hooks'
import { makeTask, page } from '../../test/factories'
import { API } from '../../test/handlers'
import { server } from '../../test/server'
import { renderWithProviders } from '../../test/utils'

function ToggleHarness({ task }: { task: ReturnType<typeof makeTask> }) {
  const mutation = useToggleTaskComplete()
  return (
    <>
      <p>{mutation.isPending ? 'Saving' : 'Ready'}</p>
      <button onClick={() => mutation.mutate(task)}>Toggle</button>
    </>
  )
}

describe('useToggleTaskComplete', () => {
  it('updates cached task lists optimistically', async () => {
    const task = makeTask({ id: 42 })
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })
    client.setQueryData(taskKeys.list({}), page([task]))
    server.use(
      http.patch(`${API}/tasks/42`, async () => {
        await new Promise((resolve) => setTimeout(resolve, 50))
        return HttpResponse.json({ ...task, status: 'done' })
      }),
    )
    renderWithProviders(<ToggleHarness task={task} />, { queryClient: client })
    fireEvent.click(screen.getByRole('button', { name: 'Toggle' }))
    await waitFor(() =>
      expect(
        client.getQueryData<{ items: (typeof task)[] }>(taskKeys.list({}))?.items[0]?.status,
      ).toBe('done'),
    )
  })

  it('rolls back the optimistic update when the request fails', async () => {
    const task = makeTask({ id: 43 })
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })
    client.setQueryData(taskKeys.list({}), page([task]))
    server.use(
      http.patch(`${API}/tasks/43`, () =>
        HttpResponse.json(
          { error: { code: 'bad_request', message: 'Failed', details: null } },
          { status: 400 },
        ),
      ),
    )
    renderWithProviders(<ToggleHarness task={task} />, { queryClient: client })
    fireEvent.click(screen.getByRole('button', { name: 'Toggle' }))
    await waitFor(() =>
      expect(
        client.getQueryData<{ items: (typeof task)[] }>(taskKeys.list({}))?.items[0]?.status,
      ).toBe('todo'),
    )
  })
})
