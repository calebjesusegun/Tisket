import { Navigate, type RouteObject } from 'react-router'
import { RouteErrorPage } from './ErrorBoundary'
import { Layout } from './Layout'
import { NotFoundPage } from './NotFoundPage'
import { PlaceholderPage } from './PlaceholderPage'

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    errorElement: <RouteErrorPage />,
    children: [
      { index: true, element: <Navigate to="/todo" replace /> },
      { path: 'todo', element: <PlaceholderPage title="ToDo" /> },
      { path: 'tasks', element: <PlaceholderPage title="Tasks" /> },
      { path: 'notes', element: <PlaceholderPage title="Notes" /> },
      { path: 'notes/new', element: <PlaceholderPage title="New note" /> },
      { path: 'notes/:noteId', element: <PlaceholderPage title="Note" /> },
      { path: 'due-soon', element: <PlaceholderPage title="Due soon" /> },
      { path: 'search', element: <PlaceholderPage title="Search" /> },
      { path: 'tags', element: <PlaceholderPage title="Tags" /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
