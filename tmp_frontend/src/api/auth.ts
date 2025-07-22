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

interface MeResponse {
  user: {
    id: string
  } | null
}

interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

type SuccessResponse = { success: boolean }

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    return api.post("auth/login", { json: credentials }).json<LoginResponse>()
  },

  logout: async (): Promise<SuccessResponse> => {
    return api.post("auth/logout").json<SuccessResponse>()
  },

  me: async (): Promise<MeResponse> => {
    return api.get("auth/me").json<MeResponse>()
  },

  changePassword: async (data: ChangePasswordRequest): Promise<SuccessResponse> => {
    return api.post("auth/change-password", { json: data }).json<SuccessResponse>()
  },
}
