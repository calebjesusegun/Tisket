import { useNavigate, useParams } from 'react-router'
import { useNote, useSaveNote } from '../hooks'
import { useTasks } from '../../tasks/hooks'
import { NoteEditor } from '../components/NoteEditor'
import { PageHeader } from '../../../app/PageHeader'
import { Button } from '../../../components/Button'
import { ErrorState, LoadingState } from '../../../components/States'
import { useDeleteNote } from '../hooks'

export function NoteEditPage() {
  const { noteId } = useParams()
  const id = noteId ? Number(noteId) : undefined
  const navigate = useNavigate()
  const note = useNote(id ?? Number.NaN)
  const tasks = useTasks({ page_size: 100 })
  const save = useSaveNote()
  const remove = useDeleteNote()
  if (id && note.isPending) return <LoadingState />
  if (id && note.isError)
    return <ErrorState message="Could not load this note." onRetry={() => void note.refetch()} />
  const current = note.data
  return (
    <>
      <PageHeader
        title={current ? 'Edit note' : 'New note'}
        actions={
          current ? (
            <Button
              variant="danger"
              onClick={() => remove.mutate(id!, { onSuccess: () => navigate('/notes') })}
            >
              Delete
            </Button>
          ) : undefined
        }
      />
      <NoteEditor
        note={current}
        tasks={tasks.data?.items ?? []}
        busy={save.isPending}
        onSave={(input) =>
          save.mutate({ input, id }, { onSuccess: (saved) => navigate(`/notes/${saved.id}`) })
        }
      />
    </>
  )
}
