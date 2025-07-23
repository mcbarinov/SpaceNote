import { api } from "./index"

export interface Space {
  id: string
  name: string
  members: string[]
  fields: unknown[]
  list_fields: string[]
  hidden_create_fields: string[]
  filters: unknown[]
  default_page_size: number
  max_page_size: number
  telegram?: unknown
}

export const spacesApi = {
  listSpaces: async (): Promise<Space[]> => {
    return await api.get("spaces").json()
  },
}
