import { fireEvent, screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'
import { NotificationBell } from './NotificationBell'
import { makeTask, page } from '../../../test/factories'
import { API } from '../../../test/handlers'
import { server } from '../../../test/server'
import { renderWithProviders } from '../../../test/utils'

describe('NotificationBell', () => {
  it('shows due tasks and supports dismissing a notification', async () => {
    const task = makeTask({ id: 201, title: 'Send the update' })
    let dismissed = false
    server.use(
      http.get(`${API}/reminders/notifications`, () =>
        HttpResponse.json(page(dismissed ? [] : [task])),
      ),
      http.post(`${API}/reminders/201/dismiss`, () => {
        dismissed = true
        return HttpResponse.json(task)
      }),
    )
    renderWithProviders(<NotificationBell />)
    const bell = await screen.findByRole('button', { name: 'Notifications, 1 due' })
    fireEvent.click(bell)
    expect(await screen.findByText('Send the update')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss' }))
    await waitFor(() => expect(screen.queryByText('Send the update')).not.toBeInTheDocument())
  })
})
