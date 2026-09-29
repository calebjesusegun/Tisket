import type { ReactNode } from 'react'
import { cn } from '../lib/cn'

type Tone = 'slate' | 'indigo' | 'green' | 'amber' | 'red' | 'sky'

const tones: Record<Tone, string> = {
  slate: 'bg-slate-100 text-slate-700',
  indigo: 'bg-indigo-50 text-indigo-700',
  green: 'bg-green-50 text-green-700',
  amber: 'bg-amber-50 text-amber-800',
  red: 'bg-red-50 text-red-700',
  sky: 'bg-sky-50 text-sky-700',
}

export function Badge({
  tone = 'slate',
  children,
  className,
}: {
  tone?: Tone
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap',
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}
