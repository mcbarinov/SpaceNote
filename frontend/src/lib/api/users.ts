import { api } from "./index"

export interface CreateUserRequest {
  username: string
  password: string
}

export const usersApi = {
  getUsers: async () => {
    return await api.get("users").json<{ id: string }[]>()
  },

  createUser: async (data: CreateUserRequest) => {
    return await api.post("users", { json: data }).json<{ id: string }>()
  },
}
