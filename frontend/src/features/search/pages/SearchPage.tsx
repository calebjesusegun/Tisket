import { Link, useSearchParams } from 'react-router'
import { PageHeader } from '../../../app/PageHeader'
import { Badge } from '../../../components/Badge'
import { SelectInput } from '../../../components/Field'
import { EmptyState, ErrorState, LoadingState } from '../../../components/States'
import { useSearch } from '../hooks'
import type { HighlightSegment, SearchType } from '../../../lib/types'

export function Highlighted({ segments }: { segments: HighlightSegment[] }) {
  return (
    <>
      {segments.map((part, index) =>
        part.match ? (
          <mark key={index} className="rounded bg-amber-200 px-0.5">
            {part.text}
          </mark>
        ) : (
          <span key={index}>{part.text}</span>
        ),
      )}
    </>
  )
}
export function SearchPage() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const type = (params.get('type') ?? 'all') as SearchType
  const result = useSearch(q, type)
  const tasks = result.data?.items.filter((item) => item.type === 'task') ?? []
  const notes = result.data?.items.filter((item) => item.type === 'note') ?? []
  const renderGroup = (heading: string, items: typeof tasks) => (
    <section key={heading}>
      <h2 className="mb-2 text-lg font-semibold">{heading}</h2>
      {items.length ? (
        <div className="space-y-2">
          {items.map((item) => (
            <Link
              key={`${item.type}-${item.id}`}
              to={item.type === 'task' ? '/tasks' : `/notes/${item.id}`}
              className="block rounded-xl border bg-white p-4 hover:border-indigo-300"
            >
              <h3 className="font-medium">
                <Highlighted segments={item.title_highlights} />
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                <Highlighted segments={item.snippet} />
              </p>
              <div className="mt-2 flex gap-1">
                {item.tags.map((tag) => (
                  <Badge key={tag.id}>#{tag.name}</Badge>
                ))}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No matching {heading.toLowerCase()}.</p>
      )}
    </section>
  )
  return (
    <>
      <PageHeader
        title="Search"
        description={q ? `Results for “${q}”` : 'Search tasks and notes from the header.'}
      />
      <div className="mb-4 max-w-xs">
        <SelectInput
          label="Search in"
          value={type}
          onChange={(e) => {
            const next = new URLSearchParams(params)
            next.set('type', e.target.value)
            setParams(next)
          }}
        >
          <option value="all">Tasks and notes</option>
          <option value="task">Tasks only</option>
          <option value="note">Notes only</option>
        </SelectInput>
      </div>
      {!q ? (
        <EmptyState
          title="Search your workspace"
          description="Enter a word or phrase in the search box above."
        />
      ) : result.isPending ? (
        <LoadingState />
      ) : result.isError ? (
        <ErrorState
          message="Search failed. Please try again."
          onRetry={() => void result.refetch()}
        />
      ) : !result.data.items.length ? (
        <EmptyState title="No matches" description="Try another search term." />
      ) : (
        <div className="space-y-6">
          {renderGroup('Tasks', tasks)}
          {renderGroup('Notes', notes)}
        </div>
      )}
    </>
  )
}
