import { Link } from "react-router"
import SpaceSelector from "./header/SpaceSelector"
import UserMenu from "./header/UserMenu"

export default function Header() {
  return (
    <header className="border-b px-6">
      <nav className="flex justify-between items-center h-14 gap-8">
        <Link to="/" className="font-bold">
          SpaceNote
        </Link>
        <SpaceSelector />
        <UserMenu />
      </nav>
    </header>
  )
}
