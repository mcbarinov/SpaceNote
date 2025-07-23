import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  sessionId: string | null
  userId: string | null
  isAuthenticated: boolean
  
  login: (sessionId: string, userId: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      sessionId: null,
      userId: null,
      isAuthenticated: false,
      
      login: (sessionId: string, userId: string) => {
        set({
          sessionId,
          userId,
          isAuthenticated: true,
        })
      },
      
      logout: () => {
        set({
          sessionId: null,
          userId: null,
          isAuthenticated: false,
        })
      },
    }),
    {
      name: 'spacenote-auth',
    }
  )
)