import { Link } from "react-router-dom"
import { useAuthStore } from "../../stores/auth"
import { authApi } from "../../api/auth"
import { Button } from "../ui/button"

export function Navigation() {
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
    <nav className="flex items-center gap-6">
      {user && <span className="text-sm text-muted-foreground">{user.id}</span>}
      <Link to="/notes" className="hover:text-accent-foreground">Notes</Link>
      <Link to="/spaces" className="hover:text-accent-foreground">Spaces</Link>
      <Link to="/admin" className="hover:text-accent-foreground">Admin</Link>
      <Link to="/profile" className="hover:text-accent-foreground">Profile</Link>
      <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
    </nav>
  )
}