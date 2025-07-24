import { api } from "./index"

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  session_id: string
  user_id: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return await api.post("auth/login", { json: data }).json()
  },

  changePassword: async (data: ChangePasswordRequest): Promise<{ message: string }> => {
    return await api
      .post("auth/change-password", {
        json: {
          current_password: data.currentPassword,
          new_password: data.newPassword,
        },
      })
      .json()
  },
}
