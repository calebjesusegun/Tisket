/* oxlint-disable react/incompatible-library -- react-hook-form owns mutable form state. */
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../../components/Button'
import { SelectInput, TextArea, TextInput } from '../../../components/Field'
import { fromLocalInput, toLocalInput } from '../../../lib/format'
import type { Task, TaskInput } from '../../../lib/types'
import { TagInput } from '../../tags/components/TagInput'

const schema = z.object({
  title: z.string().trim().min(1, 'Enter a task title').max(200),
  description: z.string().max(5000),
  priority: z.enum(['low', 'medium', 'high']),
  status: z.enum(['todo', 'in_progress', 'done']),
  due_at: z.string(),
  tags: z.array(z.string()).max(10),
})
type FormValues = z.infer<typeof schema>
export function TaskForm({
  task,
  onSubmit,
  busy,
}: {
  task?: Task
  onSubmit: (input: TaskInput) => void
  busy?: boolean
}) {
  // react-hook-form intentionally manages mutable form state and is not compiler-memoizable.
  // oxlint-disable-next-line react/incompatible-library
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: task?.title ?? '',
      description: task?.description ?? '',
      priority: task?.priority ?? 'medium',
      status: task?.status ?? 'todo',
      due_at: toLocalInput(task?.due_at ?? null),
      tags: task?.tags.map((tag) => tag.name) ?? [],
    },
  })
  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={handleSubmit((v) => onSubmit({ ...v, due_at: fromLocalInput(v.due_at) }))}
    >
      <TextInput label="Title" {...register('title')} error={errors.title?.message} />
      <TextArea
        label="Description"
        rows={3}
        {...register('description')}
        error={errors.description?.message}
      />
      <div className="grid grid-cols-2 gap-3">
        <SelectInput label="Priority" {...register('priority')}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </SelectInput>
        <SelectInput label="Status" {...register('status')}>
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </SelectInput>
      </div>
      <TextInput label="Due date and time" type="datetime-local" {...register('due_at')} />
      <TagInput
        value={watch('tags')}
        onChange={(tags) => setValue('tags', tags, { shouldValidate: true })}
      />
      <Button type="submit" disabled={busy}>
        {task ? 'Save task' : 'Create task'}
      </Button>
    </form>
  )
}
