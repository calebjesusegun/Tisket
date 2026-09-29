import { formatDateTime, formatRelative, fromLocalInput, toLocalInput } from './format'

describe('date helpers', () => {
  it('round-trips between ISO and datetime-local values', () => {
    const iso = '2026-03-01T09:30:00.000Z'
    const local = toLocalInput(iso)
    expect(local).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/)
    expect(fromLocalInput(local)).toBe(iso)
  })

  it('handles empty and invalid values', () => {
    expect(toLocalInput(null)).toBe('')
    expect(fromLocalInput('')).toBeNull()
    expect(fromLocalInput('nonsense')).toBeNull()
  })

  it('formats relative times', () => {
    const now = new Date('2026-01-15T12:00:00Z')
    expect(formatRelative('2026-01-15T12:30:00Z', now)).toBe('in 30 minutes')
    expect(formatRelative('2026-01-15T09:00:00Z', now)).toBe('3 hours ago')
    expect(formatRelative('2026-01-17T12:00:00Z', now)).toBe('in 2 days')
  })

  it('formats absolute date-times', () => {
    expect(formatDateTime('2026-01-15T12:00:00Z')).toMatch(/Jan/)
  })
})
