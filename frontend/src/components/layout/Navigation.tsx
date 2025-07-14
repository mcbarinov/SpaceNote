import { Link } from "react-router-dom"
import { UserDropdown } from "./UserDropdown"

export function Navigation() {
  return (
    <nav className="flex items-center gap-6">
      <Link to="/notes" className="hover:text-accent-foreground">Notes</Link>
      <Link to="/spaces" className="hover:text-accent-foreground">Spaces</Link>
      <Link to="/admin" className="hover:text-accent-foreground">Admin</Link>
      <UserDropdown />
    </nav>
  )
}