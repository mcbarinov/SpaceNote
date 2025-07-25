import { api } from "./index"

export interface Note {
  id: number
  author: string
  created_at: string
  edited_at?: string
  fields: Record<string, unknown>
  comment_count: number
  last_comment_at?: string
  attachment_counts?: unknown
}

export interface PaginationResult {
  notes: Note[]
  total_count: number
  current_page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface FilterCondition {
  field: string
  operator: string
  value: unknown
}

export interface Filter {
  id: string
  title: string
  description: string
  conditions: FilterCondition[]
  sort: string[]
  list_fields: string[]
}

export interface CreateNoteRequest {
  fields: Record<string, string>
}

export const notesApi = {
  listNotes: async (
    spaceId: string,
    options?: {
      filterId?: string
      page?: number
      pageSize?: number
    }
  ): Promise<PaginationResult> => {
    const searchParams = new URLSearchParams()
    searchParams.set("space_id", spaceId)
    if (options?.filterId) searchParams.set("filter_id", options.filterId)
    if (options?.page) searchParams.set("page", options.page.toString())
    if (options?.pageSize) searchParams.set("page_size", options.pageSize.toString())

    return await api.get(`notes?${searchParams.toString()}`).json()
  },

  getNote: async (spaceId: string, noteId: number): Promise<Note> => {
    const searchParams = new URLSearchParams()
    searchParams.set("space_id", spaceId)

    return await api.get(`notes/${noteId}?${searchParams.toString()}`).json()
  },

  createNote: async (spaceId: string, request: CreateNoteRequest): Promise<Note> => {
    const searchParams = new URLSearchParams()
    searchParams.set("space_id", spaceId)

    return await api.post(`notes?${searchParams.toString()}`, { json: request }).json()
  },
}
