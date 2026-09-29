import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { NoteEditor } from './NoteEditor'

describe('NoteEditor', () => {
  it('renders a safe Markdown preview', () => {
    render(<NoteEditor tasks={[]} onSave={vi.fn<() => void>()} />)
    fireEvent.change(screen.getByLabelText('Content (Markdown)'), { target: { value: '**bold**' } })
    fireEvent.click(screen.getByRole('button', { name: 'Preview' }))
    expect(screen.getByText('bold').tagName).toBe('STRONG')
  })
})
