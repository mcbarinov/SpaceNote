import { api } from "./index"
import type { Filter } from "./notes"

export type FieldType = "string" | "markdown" | "boolean" | "choice" | "tags" | "user" | "datetime" | "int" | "float" | "image"

export type FieldOption = "values" | "min" | "max"

export type FieldOptionValueType = string[] | number

export type FieldValueType = string | boolean | string[] | number | null

export interface SpaceField {
  name: string
  type: FieldType
  required: boolean
  options: Record<FieldOption, FieldOptionValueType>
  default: FieldValueType
}

export interface TelegramTemplates {
  new_note: string
  field_update: string
  comment: string
}

export interface TelegramConfig {
  enabled: boolean
  bot_id: string
  channel_id: string
  templates: TelegramTemplates
}

export interface Space {
  id: string
  name: string
  members: string[]
  fields: SpaceField[]
  list_fields: string[]
  hidden_create_fields: string[]
  filters: Filter[]
  default_page_size: number
  max_page_size: number
  telegram?: TelegramConfig
  note_detail_template?: string
  note_list_template?: string
}

export interface CreateSpaceRequest {
  id: string
  name: string
}

export interface ImportResult {
  space_id: string
  notes_imported: number
  comments_imported: number
  warnings: string[]
}

export const spacesApi = {
  listSpaces: async (): Promise<Space[]> => {
    return await api.get("spaces").json()
  },

  getSpace: async (spaceId: string): Promise<Space> => {
    return await api.get(`spaces/${spaceId}`).json()
  },

  createSpace: async (data: CreateSpaceRequest): Promise<Space> => {
    return await api.post("spaces", { json: data }).json()
  },

  updateListFields: async (spaceId: string, fieldNames: string[]): Promise<void> => {
    await api.put(`spaces/${spaceId}/list-fields`, { json: { field_names: fieldNames } })
  },

  updateHiddenCreateFields: async (spaceId: string, fieldNames: string[]): Promise<void> => {
    await api.put(`spaces/${spaceId}/hidden-create-fields`, { json: { field_names: fieldNames } })
  },

  updateNoteDetailTemplate: async (spaceId: string, template: string | null): Promise<void> => {
    await api.put(`spaces/${spaceId}/note-detail-template`, { json: { template } })
  },

  updateNoteListTemplate: async (spaceId: string, template: string | null): Promise<void> => {
    await api.put(`spaces/${spaceId}/note-list-template`, { json: { template } })
  },

  createFilter: async (spaceId: string, filter: Filter): Promise<void> => {
    await api.post(`spaces/${spaceId}/filters`, { json: filter })
  },

  deleteFilter: async (spaceId: string, filterId: string): Promise<void> => {
    await api.delete(`spaces/${spaceId}/filters/${filterId}`)
  },

  exportSpace: async (spaceId: string, includeContent: boolean = false): Promise<unknown> => {
    return await api
      .get(`spaces/${spaceId}/export`, {
        searchParams: { include_content: includeContent.toString() },
      })
      .json()
  },

  importSpace: async (data: unknown): Promise<ImportResult> => {
    return await api.post("import", { json: data }).json()
  },
}
