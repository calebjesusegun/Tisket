// Mirrors the backend Pydantic schemas (see /docs on the API).

export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface Tag {
  id: number
  name: string
}

export interface TagWithCounts extends Tag {
  task_count: number
  note_count: number
}

export interface Task {
  id: number
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  due_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
  tags: Tag[]
  is_overdue: boolean
  is_due_soon: boolean
}

export interface TaskInput {
  title: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  due_at?: string | null
  tags?: string[]
}

export type TaskSort = 'due_at' | 'priority' | 'created_at' | 'updated_at' | 'title'
export type SortOrder = 'asc' | 'desc'

export interface TaskFilters {
  status?: TaskStatus[]
  priority?: TaskPriority
  tag?: string
  sort?: TaskSort
  order?: SortOrder
  page?: number
  page_size?: number
}

export interface TaskSummary {
  id: number
  title: string
  status: TaskStatus
}

export interface Note {
  id: number
  title: string
  content: string
  pinned: boolean
  task_id: number | null
  task: TaskSummary | null
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface NoteInput {
  title: string
  content?: string
  pinned?: boolean
  task_id?: number | null
  tags?: string[]
}

export interface NoteFilters {
  tag?: string
  pinned?: boolean
  task_id?: number
  page?: number
  page_size?: number
}

export interface HighlightSegment {
  text: string
  match: boolean
}

export interface SearchResult {
  type: 'task' | 'note'
  id: number
  title: string
  title_highlights: HighlightSegment[]
  snippet: HighlightSegment[]
  tags: Tag[]
  updated_at: string
  status: TaskStatus | null
  priority: TaskPriority | null
  due_at: string | null
  pinned: boolean | null
}

export type SearchType = 'all' | 'task' | 'note'

export interface ApiErrorBody {
  error: {
    code: string
    message: string
    details: Array<{ field?: string; message: string }> | null
  }
}
