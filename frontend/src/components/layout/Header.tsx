import { Link, useNavigate } from "react-router"
import { useAuthStore } from "@/stores/authStore"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ChevronDown, User } from "lucide-react"

export default function Header() {
  const navigate = useNavigate()
  const { userId, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }
  return (
    <header className="border-b p-8">
      <nav className="flex justify-between items-center">
        <Link to="/notes" className="text-lg font-semibold">
          SpaceNote
        </Link>

        <Link to="/notes" className="hover:text-accent-foreground">
          Notes
        </Link>
        <Link to="/spaces" className="hover:text-accent-foreground">
          Spaces
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger className="flex items-center gap-1 font-medium hover:underline focus:outline-none">
            <User className="w-4 h-4" />
            {userId}
            <ChevronDown className="w-4 h-4" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" sideOffset={5}>
            <DropdownMenuItem>Change Password</DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </nav>
    </header>
  )
}
