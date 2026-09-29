import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Highlighted } from './SearchPage'

describe('search highlighting', () => {
  it('renders matching segments with mark elements', () => {
    render(
      <p>
        <Highlighted
          segments={[
            { text: 'Write ', match: false },
            { text: 'tests', match: true },
          ]}
        />
      </p>,
    )
    expect(screen.getByText('tests').tagName).toBe('MARK')
  })
})
