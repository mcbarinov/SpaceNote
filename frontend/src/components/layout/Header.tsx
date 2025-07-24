import { Link, useNavigate } from "react-router"
import { useAuthStore } from "@/stores/authStore"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ChevronDown, User } from "lucide-react"
import { useDialog } from "@/lib/dialog"

export default function Header() {
  const navigate = useNavigate()
  const { userId, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const dialog = useDialog()

  const handleChangePassword = () => {
    dialog
      .open("changePassword")
      .then(result => {
        console.log("Password change result:", result)
        // After password change, all sessions are invalidated
        // Redirect to login
        logout()
        navigate("/login")
      })
      .catch(error => {
        console.error("Password change failed:", error)
      })
  }

  const handleManageUsers = () => {
    dialog.open("userManagement")
  }

  const isAdmin = userId === "admin"
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
            <DropdownMenuItem onClick={handleChangePassword}>Change Password</DropdownMenuItem>
            {isAdmin && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleManageUsers}>Manage Users</DropdownMenuItem>
              </>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-destructive">
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </nav>
    </header>
  )
}
