import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { ErrorBoundary } from './ErrorBoundary'

let shouldThrow = true
function Bomb() {
  if (shouldThrow) throw new Error('kaboom')
  return <p>Recovered</p>
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    shouldThrow = true
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })
  afterEach(() => vi.restoreAllMocks())

  it('shows a fallback and can recover', async () => {
    const user = userEvent.setup()
    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )
    expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong')
    shouldThrow = false
    await user.click(screen.getByRole('button', { name: 'Try again' }))
    expect(screen.getByText('Recovered')).toBeInTheDocument()
  })

  it('renders children when nothing throws', () => {
    function Fine() {
      const [n] = useState(1)
      return <p>ok {n}</p>
    }
    render(
      <ErrorBoundary>
        <Fine />
      </ErrorBoundary>,
    )
    expect(screen.getByText('ok 1')).toBeInTheDocument()
  })

  it('supports a custom fallback', () => {
    render(
      <ErrorBoundary fallback={() => <p>custom</p>}>
        <Bomb />
      </ErrorBoundary>,
    )
    expect(screen.getByText('custom')).toBeInTheDocument()
  })
})
