import { api } from "./index"
import type { Filter } from "./notes"

export interface Space {
  id: string
  name: string
  members: string[]
  fields: unknown[]
  list_fields: string[]
  hidden_create_fields: string[]
  filters: Filter[]
  default_page_size: number
  max_page_size: number
  telegram?: unknown
}

export const spacesApi = {
  listSpaces: async (): Promise<Space[]> => {
    return await api.get("spaces").json()
  },

  getSpace: async (spaceId: string): Promise<Space> => {
    return await api.get(`spaces/${spaceId}`).json()
  },
}
