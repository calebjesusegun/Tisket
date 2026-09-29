import { Link } from 'react-router'
import { useState } from 'react'
import { Badge } from '../../../components/Badge'
import { SelectInput } from '../../../components/Field'
import { EmptyState, ErrorState, LoadingState } from '../../../components/States'
import { PageHeader } from '../../../app/PageHeader'
import { useNotes } from '../hooks'
import { useTags } from '../../tags/hooks'
import { formatRelative } from '../../../lib/format'

export function NotesPage() {
  const [tag, setTag] = useState('')
  const notes = useNotes(tag ? { tag } : {})
  const tags = useTags()
  return (
    <>
      <PageHeader
        title="Notes"
        description="Ideas, meeting notes, and reference material."
        actions={
          <Link
            className="inline-flex h-10 items-center rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white hover:bg-indigo-700"
            to="/notes/new"
          >
            New note
          </Link>
        }
      />
      <div className="mb-4 max-w-xs">
        <SelectInput label="Filter by tag" value={tag} onChange={(e) => setTag(e.target.value)}>
          <option value="">All tags</option>
          {tags.data?.map((item) => (
            <option key={item.id}>{item.name}</option>
          ))}
        </SelectInput>
      </div>
      {notes.isPending ? (
        <LoadingState />
      ) : notes.isError ? (
        <ErrorState message="Could not load notes." onRetry={() => void notes.refetch()} />
      ) : notes.data.items.length === 0 ? (
        <EmptyState
          title="No notes yet"
          description="Create a note to keep useful information close."
          action={
            <Link className="text-indigo-700" to="/notes/new">
              Create your first note
            </Link>
          }
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {notes.data.items.map((note) => (
            <Link
              key={note.id}
              to={`/notes/${note.id}`}
              className="rounded-xl border border-slate-200 bg-white p-4 hover:border-indigo-300"
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-semibold">
                  {note.pinned ? '📌 ' : ''}
                  {note.title}
                </h2>
                <span className="shrink-0 text-xs text-slate-500">
                  {formatRelative(note.updated_at)}
                </span>
              </div>
              <p className="mt-2 line-clamp-3 text-sm whitespace-pre-wrap text-slate-600">
                {note.content}
              </p>
              <div className="mt-3 flex flex-wrap gap-1">
                {note.tags.map((item) => (
                  <Badge key={item.id}>#{item.name}</Badge>
                ))}
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  )
}
