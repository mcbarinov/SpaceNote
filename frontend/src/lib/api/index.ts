import ky from "ky"
import { useAuthStore } from "../../stores/authStore"
import { toast } from "sonner"
import type { ApiErrorResponse } from "@/lib/errors"

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
          return
        }

        if (!response.ok) {
          try {
            const errorData = (await response.json()) as ApiErrorResponse
            toast.error(errorData.detail || "An error occurred")
          } catch {
            toast.error("Failed to parse server response")
          }
        }
      },
    ],
    beforeError: [
      error => {
        // Only show network error if there's no response (actual network failure)
        if (!error.response) {
          toast.error("Connection failed. Please check your internet connection.")
        }
        return error
      },
    ],
  },
})

// Re-export all APIs
export * from "./auth"
export * from "./notes"
export * from "./spaces"
export * from "./users"
