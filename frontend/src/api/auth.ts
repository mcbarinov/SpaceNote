import api from "./client"

interface LoginRequest {
  username: string
  password: string
}

interface LoginResponse {
  session_id: string
  user: {
    id: string
  }
}

interface LogoutResponse {
  success: boolean
}

interface MeResponse {
  user: {
    id: string
  } | null
}

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    return api.post("auth/login", { json: credentials }).json<LoginResponse>()
  },

  logout: async (): Promise<LogoutResponse> => {
    return api.post("auth/logout").json<LogoutResponse>()
  },

  me: async (): Promise<MeResponse> => {
    return api.get("auth/me").json<MeResponse>()
  },
}
