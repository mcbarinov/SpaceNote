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
}

export interface CreateSpaceRequest {
  id: string
  name: string
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
}
