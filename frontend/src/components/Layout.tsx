import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { useAuthStore } from "../stores/auth"
import { authApi } from "../api/auth"
import { Button } from "./ui/button"

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      logout()
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-2xl font-bold">SpaceNote</h1>
          
          <nav className="flex items-center gap-6">
            {user && <span className="text-sm text-muted-foreground">{user.id}</span>}
            <Link to="/notes" className="hover:text-accent-foreground">Notes</Link>
            <Link to="/spaces" className="hover:text-accent-foreground">Spaces</Link>
            <Link to="/admin" className="hover:text-accent-foreground">Admin</Link>
            <Link to="/profile" className="hover:text-accent-foreground">Profile</Link>
            <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
          </nav>
        </div>
      </header>

      <main className="flex-1 bg-muted/50">
        <div className="container mx-auto px-4 py-8">
          {children}
        </div>
      </main>

      <footer className="border-t bg-background">
        <div className="container mx-auto px-4 py-6 text-center">
          <p className="text-sm text-muted-foreground">SpaceNote v0.0.8</p>
        </div>
      </footer>
    </div>
  )
}