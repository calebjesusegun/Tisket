import { render, screen } from '@testing-library/react'
import { App } from './App'

describe('App', () => {
  it('redirects / to the ToDo page inside the layout', async () => {
    render(<App />)
    expect(await screen.findByRole('heading', { name: 'ToDo' })).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'Main' })).toBeInTheDocument()
    expect(screen.getByRole('searchbox', { name: 'Search tasks and notes' })).toBeInTheDocument()
  })
})
