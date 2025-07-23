import { api } from "./index"

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
