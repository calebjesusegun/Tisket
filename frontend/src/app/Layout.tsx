import type { ReactNode } from 'react'
import { NavLink, Outlet } from 'react-router'
import { CheckSquareIcon } from '../components/icons'
import { cn } from '../lib/cn'
import { SearchBox } from '../features/search/components/SearchBox'
import { NAV_ITEMS } from './nav'

interface LayoutProps {
  /** Rendered in the header next to the search box (e.g. the notification bell). */
  headerActions?: ReactNode
}

export function Layout({ headerActions }: LayoutProps) {
  return (
    <div className="min-h-dvh bg-slate-50 text-slate-900">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded focus:bg-white focus:px-3 focus:py-2 focus:shadow"
      >
        Skip to content
      </a>

      <aside className="fixed inset-y-0 left-0 hidden w-56 flex-col border-r border-slate-200 bg-white px-3 py-5 md:flex">
        <NavLink
          to="/todo"
          className="mb-6 flex items-center gap-2 px-3 text-lg font-bold text-indigo-600"
        >
          <CheckSquareIcon width={22} height={22} /> Tisket
        </NavLink>
        <nav aria-label="Main" className="flex flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                )
              }
            >
              <Icon /> {label}
            </NavLink>
          ))}
        </nav>
        <p className="mt-auto px-3 text-xs text-slate-400">Shared workspace · no login</p>
      </aside>

      <div className="md:pl-56">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur md:px-8">
          <NavLink
            to="/todo"
            className="text-lg font-bold text-indigo-600 md:hidden"
            aria-label="Tisket home"
          >
            Tisket
          </NavLink>
          <SearchBox />
          <div className="ml-auto flex items-center gap-2">{headerActions}</div>
        </header>

        <main id="main" className="mx-auto w-full max-w-4xl px-4 pt-6 pb-28 md:px-8 md:pb-12">
          <Outlet />
        </main>
      </div>

      <nav
        aria-label="Mobile"
        className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 border-t border-slate-200 bg-white pb-[env(safe-area-inset-bottom)] md:hidden"
      >
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium',
                isActive ? 'text-indigo-600' : 'text-slate-500',
              )
            }
          >
            <Icon /> {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
