import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate, useSearchParams } from 'react-router'
import { SearchIcon } from '../../../components/icons'

/** Global search box in the header. Submitting navigates to /search?q=… */
export function SearchBox() {
  const location = useLocation()
  const [params] = useSearchParams()
  const current = location.pathname === '/search' ? (params.get('q') ?? '') : ''
  // Remount when the URL query changes so the input always reflects it.
  return <SearchForm key={current} initial={current} />
}

function SearchForm({ initial }: { initial: string }) {
  const navigate = useNavigate()
  const [value, setValue] = useState(initial)

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    const q = value.trim()
    if (q) navigate(`/search?q=${encodeURIComponent(q)}`)
  }

  return (
    <form role="search" onSubmit={onSubmit} className="relative w-full max-w-md">
      <label htmlFor="global-search" className="sr-only">
        Search tasks and notes
      </label>
      <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
        <SearchIcon />
      </span>
      <input
        id="global-search"
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search tasks and notes…"
        autoComplete="off"
        className="h-10 w-full rounded-lg border border-slate-300 bg-white pr-3 pl-9 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none"
      />
    </form>
  )
}
