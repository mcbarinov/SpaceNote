import { create } from "zustand"
import { persist } from "zustand/middleware"

interface User {
  id: string
}

interface AuthState {
  user: User | null
  sessionId: string | null
  isAuthenticated: boolean
  login: (sessionId: string, user: User) => void
  logout: () => void
  setUser: (user: User | null) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      sessionId: null,
      isAuthenticated: false,

      login: (sessionId: string, user: User) => {
        set({
          sessionId,
          user,
          isAuthenticated: true,
        })
      },

      logout: () => {
        set({
          sessionId: null,
          user: null,
          isAuthenticated: false,
        })
      },

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        })
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        sessionId: state.sessionId,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)
