import { useState, type KeyboardEvent } from 'react'
import { TextInput } from '../../../components/Field'
import { Button } from '../../../components/Button'
import { Badge } from '../../../components/Badge'

export function TagInput({
  value,
  onChange,
  label = 'Tags',
}: {
  value: string[]
  onChange: (tags: string[]) => void
  label?: string
}) {
  const [draft, setDraft] = useState('')
  const add = (raw: string) => {
    const name = raw.trim().toLowerCase().replace(/\s+/g, '-')
    if (name && !value.includes(name)) onChange([...value, name])
    setDraft('')
  }
  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      add(draft)
    } else if (event.key === 'Backspace' && !draft && value.length) onChange(value.slice(0, -1))
  }
  return (
    <div>
      <div className="flex gap-2">
        <TextInput
          label={label}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          onBlur={() => draft && add(draft)}
          placeholder="Type a tag and press Enter"
        />
        <Button type="button" variant="secondary" className="mt-6" onClick={() => add(draft)}>
          Add
        </Button>
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {value.map((tag) => (
          <span key={tag} className="inline-flex items-center gap-1">
            <Badge>#{tag}</Badge>
            <button
              type="button"
              aria-label={`Remove ${tag}`}
              onClick={() => onChange(value.filter((item) => item !== tag))}
              className="text-slate-500"
            >
              ×
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}
