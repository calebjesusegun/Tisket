import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { cn } from '../lib/cn'
import { ToastContext, type ToastTone } from './toast-context'

interface Toast {
  id: number
  message: string
  tone: ToastTone
}

let nextId = 1

const toneClass: Record<ToastTone, string> = {
  info: 'border-slate-200 bg-white text-slate-800',
  success: 'border-green-200 bg-green-50 text-green-800',
  error: 'border-red-200 bg-red-50 text-red-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-900',
}

export function ToastProvider({
  children,
  duration = 5000,
}: {
  children: ReactNode
  duration?: number
}) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((t) => t.id !== id))
  }, [])

  const notify = useCallback(
    (message: string, tone: ToastTone = 'info') => {
      const id = nextId++
      setToasts((current) => [...current.slice(-3), { id, message, tone }])
      window.setTimeout(() => dismiss(id), duration)
    },
    [dismiss, duration],
  )

  const value = useMemo(() => ({ notify }), [notify])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        aria-live="polite"
        className="pointer-events-none fixed inset-x-0 bottom-20 z-50 flex flex-col items-center gap-2 px-4 sm:bottom-6 sm:items-end"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={cn(
              'pointer-events-auto flex w-full max-w-sm items-start justify-between gap-3 rounded-xl border px-4 py-3 text-sm shadow-lg',
              toneClass[toast.tone],
            )}
          >
            <span>{toast.message}</span>
            <button
              type="button"
              className="text-xs font-medium opacity-70 hover:opacity-100"
              onClick={() => dismiss(toast.id)}
            >
              Close
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
