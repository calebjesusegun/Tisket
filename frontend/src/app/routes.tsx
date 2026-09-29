import { Navigate, type RouteObject } from 'react-router'
import { RouteErrorPage } from './ErrorBoundary'
import { Layout } from './Layout'
import { NotFoundPage } from './NotFoundPage'
import { TodoPage } from '../features/tasks/pages/TodoPage'
import { TasksPage } from '../features/tasks/pages/TasksPage'
import { NotesPage } from '../features/notes/pages/NotesPage'
import { NoteEditPage } from '../features/notes/pages/NoteEditPage'
import { DueSoonPage } from '../features/reminders/pages/DueSoonPage'
import { SearchPage } from '../features/search/pages/SearchPage'
import { TagsPage } from '../features/tags/pages/TagsPage'
import { NotificationBell } from '../features/reminders/components/NotificationBell'

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Layout headerActions={<NotificationBell />} />,
    errorElement: <RouteErrorPage />,
    children: [
      { index: true, element: <Navigate to="/todo" replace /> },
      { path: 'todo', element: <TodoPage /> },
      { path: 'tasks', element: <TasksPage /> },
      { path: 'notes', element: <NotesPage /> },
      { path: 'notes/new', element: <NoteEditPage /> },
      { path: 'notes/:noteId', element: <NoteEditPage /> },
      { path: 'due-soon', element: <DueSoonPage /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'tags', element: <TagsPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
