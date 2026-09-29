import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderRoute } from '../test/utils'

describe('Layout', () => {
  it('shows desktop and mobile navigation with the active page marked', async () => {
    renderRoute({ route: '/notes' })
    const main = screen.getByRole('navigation', { name: 'Main' })
    const mobile = screen.getByRole('navigation', { name: 'Mobile' })
    for (const label of ['ToDo', 'Tasks', 'Notes', 'Due soon', 'Tags']) {
      expect(within(main).getByRole('link', { name: label })).toBeInTheDocument()
      expect(within(mobile).getByRole('link', { name: label })).toBeInTheDocument()
    }
    expect(within(main).getByRole('link', { name: 'Notes' })).toHaveAttribute(
      'aria-current',
      'page',
    )
  })

  it('navigates with the nav links', async () => {
    const user = userEvent.setup()
    const { router } = renderRoute({ route: '/todo' })
    await user.click(
      within(screen.getByRole('navigation', { name: 'Main' })).getByRole('link', { name: 'Tags' }),
    )
    expect(router.state.location.pathname).toBe('/tags')
  })

  it('submits the search box to the search page', async () => {
    const user = userEvent.setup()
    const { router } = renderRoute({ route: '/todo' })
    const box = screen.getByRole('searchbox', { name: 'Search tasks and notes' })
    await user.type(box, '  groceries list {Enter}')
    expect(router.state.location.pathname).toBe('/search')
    expect(router.state.location.search).toBe('?q=groceries%20list')
  })

  it('ignores blank searches and pre-fills from the URL', async () => {
    const user = userEvent.setup()
    const { router } = renderRoute({ route: '/search?q=milk' })
    const box = screen.getByRole('searchbox', { name: 'Search tasks and notes' })
    expect(box).toHaveValue('milk')
    await user.clear(box)
    await user.type(box, '   {Enter}')
    expect(router.state.location.search).toBe('?q=milk')
  })

  it('shows a not found page for unknown routes', () => {
    renderRoute({ route: '/does-not-exist' })
    expect(screen.getByText('Page not found')).toBeInTheDocument()
  })
})
