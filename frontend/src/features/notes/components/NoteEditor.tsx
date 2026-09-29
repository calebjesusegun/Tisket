import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '../../../components/Button'
import { SelectInput, TextArea, TextInput } from '../../../components/Field'
import { TagInput } from '../../tags/components/TagInput'
import type { Note, NoteInput, Task } from '../../../lib/types'

export function NoteEditor({
  note,
  tasks,
  onSave,
  busy,
}: {
  note?: Note
  tasks: Task[]
  onSave: (input: NoteInput) => void
  busy?: boolean
}) {
  const [title, setTitle] = useState(note?.title ?? '')
  const [content, setContent] = useState(note?.content ?? '')
  const [tags, setTags] = useState(note?.tags.map((tag) => tag.name) ?? [])
  const [taskId, setTaskId] = useState(note?.task_id?.toString() ?? '')
  const [pinned, setPinned] = useState(note?.pinned ?? false)
  const [preview, setPreview] = useState(false)
  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={(e) => {
        e.preventDefault()
        onSave({
          title: title.trim(),
          content,
          tags,
          pinned,
          task_id: taskId ? Number(taskId) : null,
        })
      }}
    >
      <TextInput
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        maxLength={200}
      />
      <div className="flex gap-2">
        <Button
          size="sm"
          variant={preview ? 'secondary' : 'primary'}
          onClick={() => setPreview(false)}
        >
          Write
        </Button>
        <Button
          size="sm"
          variant={preview ? 'primary' : 'secondary'}
          onClick={() => setPreview(true)}
        >
          Preview
        </Button>
      </div>
      {preview ? (
        <article className="prose min-h-48 max-w-none rounded-lg border p-4">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </article>
      ) : (
        <TextArea
          label="Content (Markdown)"
          rows={12}
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
      )}
      <TagInput value={tags} onChange={setTags} />
      <SelectInput label="Linked task" value={taskId} onChange={(e) => setTaskId(e.target.value)}>
        <option value="">No linked task</option>
        {tasks.map((task) => (
          <option value={task.id} key={task.id}>
            {task.title}
          </option>
        ))}
      </SelectInput>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={pinned} onChange={(e) => setPinned(e.target.checked)} />
        Pin note
      </label>
      <Button type="submit" disabled={!title.trim() || busy}>
        {note ? 'Save note' : 'Create note'}
      </Button>
    </form>
  )
}
