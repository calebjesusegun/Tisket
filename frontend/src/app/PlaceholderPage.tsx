import { PageHeader } from './PageHeader'

/** Temporary page used until the feature is built (Phase 6). */
export function PlaceholderPage({ title }: { title: string }) {
  return <PageHeader title={title} description="Coming soon." />
}
