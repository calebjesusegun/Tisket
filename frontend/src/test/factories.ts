import type { Note, Page, Tag, Task } from '../lib/types'

let id = 100

export function makeTag(overrides: Partial<Tag> = {}): Tag {
  return { id: ++id, name: 'work', ...overrides }
}

export function makeTask(overrides: Partial<Task> = {}): Task {
  return {
    id: ++id,
    title: 'Write tests',
    description: '',
    status: 'todo',
    priority: 'medium',
    due_at: null,
    completed_at: null,
    created_at: '2026-01-15T12:00:00Z',
    updated_at: '2026-01-15T12:00:00Z',
    tags: [],
    is_overdue: false,
    is_due_soon: false,
    ...overrides,
  }
}

export function makeNote(overrides: Partial<Note> = {}): Note {
  return {
    id: ++id,
    title: 'Meeting notes',
    content: '# Agenda',
    pinned: false,
    task_id: null,
    task: null,
    tags: [],
    created_at: '2026-01-15T12:00:00Z',
    updated_at: '2026-01-15T12:00:00Z',
    ...overrides,
  }
}

export function page<T>(items: T[], overrides: Partial<Page<T>> = {}): Page<T> {
  return {
    items,
    total: items.length,
    page: 1,
    page_size: 20,
    pages: items.length ? 1 : 0,
    ...overrides,
  }
}
