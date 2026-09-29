import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { TaskForm } from './TaskForm'
import { renderWithProviders } from '../../../test/utils'

describe('TaskForm', () => {
  it('requires a non-empty title before saving', async () => {
    const onSubmit = vi.fn<() => void>()
    renderWithProviders(<TaskForm onSubmit={onSubmit} />)
    fireEvent.click(screen.getByRole('button', { name: 'Create task' }))
    expect(await screen.findByText('Enter a task title')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
