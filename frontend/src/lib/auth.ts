import { redirect } from "react-router"
import { useAuthStore } from "../stores/authStore"

export function requireAuth() {
  const isAuthenticated = useAuthStore.getState().isAuthenticated
  if (!isAuthenticated) {
    throw redirect("/login")
  }
  return null
}
