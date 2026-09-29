import { CheckSquareIcon, ClockIcon, ListIcon, NoteIcon, TagIcon } from '../components/icons'

export const NAV_ITEMS = [
  { to: '/todo', label: 'ToDo', icon: CheckSquareIcon },
  { to: '/tasks', label: 'Tasks', icon: ListIcon },
  { to: '/notes', label: 'Notes', icon: NoteIcon },
  { to: '/due-soon', label: 'Due soon', icon: ClockIcon },
  { to: '/tags', label: 'Tags', icon: TagIcon },
] as const
