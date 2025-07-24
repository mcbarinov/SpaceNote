import ky from "ky"
import { useAuthStore } from "../../stores/authStore"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000/api"

export const api = ky.create({
  prefixUrl: API_URL,
  hooks: {
    beforeRequest: [
      request => {
        const sessionId = useAuthStore.getState().sessionId
        if (sessionId) {
          request.headers.set("X-Session-ID", sessionId)
        }
      },
    ],
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

// Re-export all APIs
export * from "./auth"
export * from "./notes"
export * from "./spaces"
export * from "./users"
