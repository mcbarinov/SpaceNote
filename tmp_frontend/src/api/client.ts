import ky from "ky"

const api = ky.create({
  prefixUrl: "/new-api",
  credentials: "include",
  timeout: 10000,
})

export default api
