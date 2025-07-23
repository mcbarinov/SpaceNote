import { Outlet, Link, useNavigate } from "react-router"
import { useAuthStore } from "../stores/authStore"
import { Button } from "./ui/button"

export default function Layout() {
  const navigate = useNavigate()
  const { userId, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b p-4">
        <nav className="flex justify-between items-center">
          <Link to="/notes" className="text-lg font-semibold">SpaceNote</Link>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, {userId}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </nav>
      </header>

      <main className="flex-1 p-8">
        <Outlet />
      </main>

      <footer className="border-t p-4 text-center">
        <p>© 2025 SpaceNote</p>
      </footer>
    </div>
  )
}