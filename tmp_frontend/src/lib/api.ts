import ky from "ky"
import { useAuthStore } from "@/stores/auth"

const LEGACY_BASE_URL = "http://localhost:3000"

export const api = ky.extend({
  prefixUrl: "/new-api",
  credentials: "include",
  hooks: {
    afterResponse: [
      async (_request, _options, response) => {
        if (response.status === 401) {
          useAuthStore.getState().logout()
          window.location.href = "/login"
        }
      },
    ],
  },
})

// Simplified types for prototyping - only what we actually use
export interface Space {
  id: string
  name: string
  members: string[]
  fields: unknown[]
  filters: unknown[]
  telegram: { enabled: boolean } | null
}

export const spacesApi = {
  list: () => api.get("spaces").json<Space[]>(),
}

export { LEGACY_BASE_URL }