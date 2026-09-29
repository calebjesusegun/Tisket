import { useState } from 'react'
import { Button } from '../../../components/Button'
import { TextInput } from '../../../components/Field'
import { EmptyState, ErrorState, LoadingState } from '../../../components/States'
import { PageHeader } from '../../../app/PageHeader'
import { useDeleteTag, useRenameTag, useTags } from '../hooks'

export function TagsPage() {
  const tags = useTags()
  const rename = useRenameTag()
  const remove = useDeleteTag()
  const [names, setNames] = useState<Record<number, string>>({})
  return (
    <>
      <PageHeader title="Tags" description="Manage labels used across tasks and notes." />
      {tags.isPending ? (
        <LoadingState />
      ) : tags.isError ? (
        <ErrorState message="Could not load tags." onRetry={() => void tags.refetch()} />
      ) : tags.data.length === 0 ? (
        <EmptyState
          title="No tags yet"
          description="Tags are created when you add them to a task or note."
        />
      ) : (
        <div className="divide-y rounded-xl border border-slate-200 bg-white">
          {tags.data.map((tag) => (
            <div key={tag.id} className="flex flex-wrap items-center gap-2 p-3">
              <div className="flex-1">
                <TextInput
                  label={`Tag ${tag.name}`}
                  hideLabel
                  value={names[tag.id] ?? tag.name}
                  onChange={(e) => setNames({ ...names, [tag.id]: e.target.value })}
                />
                <p className="mt-1 text-xs text-slate-500">
                  {tag.task_count} tasks · {tag.note_count} notes
                </p>
              </div>
              <Button
                size="sm"
                variant="secondary"
                disabled={!names[tag.id] || names[tag.id] === tag.name || rename.isPending}
                onClick={() => rename.mutate({ id: tag.id, name: names[tag.id] ?? tag.name })}
              >
                Rename
              </Button>
              <Button size="sm" variant="danger" onClick={() => remove.mutate(tag.id)}>
                Delete
              </Button>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
