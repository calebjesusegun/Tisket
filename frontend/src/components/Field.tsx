import { useId, type ReactNode, type Ref } from 'react'
import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'
import { cn } from '../lib/cn'

const control =
  'w-full rounded-lg border bg-white px-3 text-sm text-slate-900 placeholder:text-slate-400 ' +
  'focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none ' +
  'disabled:bg-slate-50'

interface FieldProps {
  label: string
  error?: string
  hint?: string
  hideLabel?: boolean
  children: (props: { id: string; describedBy?: string; invalid: boolean }) => ReactNode
}

/** Label + control + hint/error, wired up with ids for accessibility. */
export function Field({ label, error, hint, hideLabel, children }: FieldProps) {
  const id = useId()
  const messageId = `${id}-message`
  const message = error ?? hint
  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={id}
        className={cn('text-sm font-medium text-slate-700', hideLabel && 'sr-only')}
      >
        {label}
      </label>
      {children({ id, describedBy: message ? messageId : undefined, invalid: Boolean(error) })}
      {message && (
        <p
          id={messageId}
          className={cn('text-xs', error ? 'text-red-600' : 'text-slate-500')}
          role={error ? 'alert' : undefined}
        >
          {message}
        </p>
      )}
    </div>
  )
}

type Common = { label: string; error?: string; hint?: string; hideLabel?: boolean }

export function TextInput({
  label,
  error,
  hint,
  hideLabel,
  className,
  ref,
  ...props
}: Common & InputHTMLAttributes<HTMLInputElement> & { ref?: Ref<HTMLInputElement> }) {
  return (
    <Field label={label} error={error} hint={hint} hideLabel={hideLabel}>
      {({ id, describedBy, invalid }) => (
        <input
          id={id}
          ref={ref}
          aria-invalid={invalid || undefined}
          aria-describedby={describedBy}
          className={cn(
            control,
            'h-10',
            invalid ? 'border-red-400' : 'border-slate-300',
            className,
          )}
          {...props}
        />
      )}
    </Field>
  )
}

export function TextArea({
  label,
  error,
  hint,
  hideLabel,
  className,
  ref,
  ...props
}: Common & TextareaHTMLAttributes<HTMLTextAreaElement> & { ref?: Ref<HTMLTextAreaElement> }) {
  return (
    <Field label={label} error={error} hint={hint} hideLabel={hideLabel}>
      {({ id, describedBy, invalid }) => (
        <textarea
          id={id}
          ref={ref}
          aria-invalid={invalid || undefined}
          aria-describedby={describedBy}
          className={cn(
            control,
            'py-2',
            invalid ? 'border-red-400' : 'border-slate-300',
            className,
          )}
          {...props}
        />
      )}
    </Field>
  )
}

export function SelectInput({
  label,
  error,
  hint,
  hideLabel,
  className,
  children,
  ref,
  ...props
}: Common & SelectHTMLAttributes<HTMLSelectElement> & { ref?: Ref<HTMLSelectElement> }) {
  return (
    <Field label={label} error={error} hint={hint} hideLabel={hideLabel}>
      {({ id, describedBy, invalid }) => (
        <select
          id={id}
          ref={ref}
          aria-invalid={invalid || undefined}
          aria-describedby={describedBy}
          className={cn(
            control,
            'h-10',
            invalid ? 'border-red-400' : 'border-slate-300',
            className,
          )}
          {...props}
        >
          {children}
        </select>
      )}
    </Field>
  )
}
