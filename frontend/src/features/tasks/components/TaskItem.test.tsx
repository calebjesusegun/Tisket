import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { TaskItem } from './TaskItem'
import { makeTask } from '../../../test/factories'

describe('TaskItem', () => {
  it('shows due tasks and toggles completion', () => {
    const onToggle = vi.fn<() => void>()
    render(
      <TaskItem task={makeTask({ title: 'Ship feature', is_overdue: true })} onToggle={onToggle} />,
    )
    expect(screen.getByText('Overdue')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('checkbox', { name: 'Complete Ship feature' }))
    expect(onToggle).toHaveBeenCalledOnce()
  })
})
