import ky from "ky"
import { useAuthStore } from "../stores/authStore"

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
      async (request, options, response) => {
        if (response.status === 401) {
          useAuthStore.getState().logout()
          window.location.href = "/login"
        }
      },
    ],
  },
})

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  session_id: string
  user_id: string
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return await api.post("auth/login", { json: data }).json()
  },
}
