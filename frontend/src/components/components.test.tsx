import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'
import { SelectInput, TextArea, TextInput } from './Field'
import { Modal } from './Modal'
import { EmptyState, ErrorState, LoadingState } from './States'
import { ToastProvider } from './Toast'
import { useToast } from './toast-context'

describe('Field inputs', () => {
  it('link label, hint and error for assistive tech', () => {
    render(
      <>
        <TextInput label="Title" error="Title is required" />
        <TextArea label="Body" hint="Markdown supported" />
        <SelectInput label="Priority">
          <option>low</option>
        </SelectInput>
      </>,
    )
    const title = screen.getByLabelText('Title')
    expect(title).toHaveAttribute('aria-invalid', 'true')
    expect(title).toHaveAccessibleDescription('Title is required')
    expect(screen.getByRole('alert')).toHaveTextContent('Title is required')
    expect(screen.getByLabelText('Body')).toHaveAccessibleDescription('Markdown supported')
    expect(screen.getByLabelText('Priority')).not.toHaveAttribute('aria-invalid')
  })
})

describe('Modal', () => {
  it('renders nothing when closed', () => {
    render(
      <Modal open={false} title="Edit" onClose={() => {}}>
        body
      </Modal>,
    )
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('focuses the first field and closes with Escape or the close button', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn<() => void>()
    render(
      <Modal open title="Edit task" onClose={onClose}>
        <input aria-label="Name" />
      </Modal>,
    )
    expect(screen.getByRole('dialog', { name: 'Edit task' })).toBeInTheDocument()
    expect(screen.getByLabelText('Name')).toHaveFocus()
    await user.keyboard('{Escape}')
    await user.click(screen.getByRole('button', { name: 'Close' }))
    expect(onClose).toHaveBeenCalledTimes(2)
  })
})

describe('States', () => {
  it('render loading, empty and error states', async () => {
    const user = userEvent.setup()
    const retry = vi.fn<() => void>()
    render(
      <>
        <LoadingState label="Loading tasks" />
        <EmptyState title="No tasks" description="Add one" action={<Button>Add</Button>} />
        <ErrorState message="Failed" onRetry={retry} />
      </>,
    )
    expect(screen.getByRole('status')).toHaveTextContent('Loading tasks')
    expect(screen.getByText('No tasks')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Try again' }))
    expect(retry).toHaveBeenCalled()
  })
})

describe('Toast', () => {
  function Trigger() {
    const { notify } = useToast()
    return <Button onClick={() => notify('Saved!', 'success')}>Save</Button>
  }

  it('shows and dismisses notifications', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider>
        <Trigger />
      </ToastProvider>,
    )
    await user.click(screen.getByRole('button', { name: 'Save' }))
    expect(screen.getByText('Saved!')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Close' }))
    expect(screen.queryByText('Saved!')).not.toBeInTheDocument()
  })

  it('throws a helpful error outside the provider', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => render(<Trigger />)).toThrow('useToast must be used inside <ToastProvider>')
    vi.restoreAllMocks()
  })
})
