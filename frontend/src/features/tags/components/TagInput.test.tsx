import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { TagInput } from './TagInput'

describe('TagInput', () => {
  it('normalizes tags, adds with Enter, and removes with Backspace', () => {
    const onChange = vi.fn<(tags: string[]) => void>()
    render(<TagInput value={[]} onChange={onChange} />)
    const input = screen.getByLabelText('Tags')
    fireEvent.change(input, { target: { value: 'Team Notes' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(onChange).toHaveBeenLastCalledWith(['team-notes'])
    onChange.mockClear()
    render(<TagInput value={['work']} onChange={onChange} />)
    fireEvent.keyDown(screen.getAllByLabelText('Tags')[1]!, { key: 'Backspace' })
    expect(onChange).toHaveBeenCalledWith([])
  })
})
