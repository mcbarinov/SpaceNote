import { type ReactNode, useEffect } from "react"
import { Navigate } from "react-router-dom"
import { useAuthStore } from "../stores/auth"
import { authApi } from "../api/auth"

interface ProtectedRouteProps {
  children: ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, setUser, sessionId } = useAuthStore()

  useEffect(() => {
    const checkAuth = async () => {
      if (sessionId) {
        try {
          const response = await authApi.me()
          setUser(response.user)
        } catch (error) {
          console.error("Auth check failed:", error)
          setUser(null)
        }
      }
    }

    checkAuth()
  }, [sessionId, setUser])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
