import { Component, type ErrorInfo, type ReactNode } from 'react'
import { isRouteErrorResponse, useRouteError } from 'react-router'
import { Button } from '../components/Button'

interface Props {
  children: ReactNode
  fallback?: (reset: () => void) => ReactNode
}
interface State {
  error: Error | null
}

function Fallback({ onReset, detail }: { onReset?: () => void; detail?: string }) {
  return (
    <div
      role="alert"
      className="mx-auto flex max-w-md flex-col items-center gap-3 px-6 py-16 text-center"
    >
      <h1 className="text-xl font-semibold text-slate-900">Something went wrong</h1>
      <p className="text-sm text-slate-600">
        {detail ?? 'An unexpected error happened. Your data is safe; try again.'}
      </p>
      <div className="flex gap-2">
        {onReset && <Button onClick={onReset}>Try again</Button>}
        <Button variant="secondary" onClick={() => window.location.assign('/')}>
          Go home
        </Button>
      </div>
    </div>
  )
}

/** Catches render errors anywhere below it and shows a recoverable fallback. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled UI error', error, info.componentStack)
  }

  reset = () => this.setState({ error: null })

  render() {
    if (this.state.error) {
      return this.props.fallback ? (
        this.props.fallback(this.reset)
      ) : (
        <Fallback onReset={this.reset} />
      )
    }
    return this.props.children
  }
}

/** errorElement for the router (errors thrown by routes/loaders). */
export function RouteErrorPage() {
  const error = useRouteError()
  const detail = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : error instanceof Error
      ? error.message
      : undefined
  return <Fallback detail={detail} />
}
