import { Outlet, Link } from "react-router"

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b p-4">
        <nav className="flex justify-between">
          <Link to="/notes">SpaceNote</Link>
          <Link to="/login">Logout</Link>
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