import { render, screen } from '@testing-library/react'
import { App } from './App'
import { createTestQueryClient } from '../test/utils'

describe('App', () => {
  it('redirects / to the ToDo page inside the layout', async () => {
    render(<App queryClient={createTestQueryClient()} />)
    expect(await screen.findByRole('heading', { name: 'ToDo' })).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'Main' })).toBeInTheDocument()
  })
})
