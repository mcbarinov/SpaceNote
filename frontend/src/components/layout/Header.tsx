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
    <header className="border-b px-6">
      <nav className="flex justify-center items-center h-14 gap-8">
        <Link to="/notes" className="font-bold">
          SpaceNote
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger className="flex items-center gap-2">
            <User className="w-4 h-4" />
            {userId}
            <ChevronDown className="w-3 h-3" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Spaces</DropdownMenuItem>
            <DropdownMenuItem>Change Password</DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout} className="text-destructive">
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </nav>
    </header>
  )
}
