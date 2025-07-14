import { useState } from "react"
import { User, ChevronDown, KeyIcon, LogOutIcon } from "lucide-react"
import { useAuthStore } from "../../stores/auth"
import { authApi } from "../../api/auth"
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu"
import { Button } from "../ui/button"
import { ChangePasswordDialog } from "../auth/ChangePasswordDialog"

export function UserDropdown() {
  const { user, logout } = useAuthStore()
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false)

  if (!user) return null

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="flex items-center gap-2 px-3">
            <User className="h-4 w-4" />
            <span className="text-sm">{user.id}</span>
            <ChevronDown className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuItem onClick={() => setIsChangePasswordOpen(true)}>
            <KeyIcon className="mr-2 h-4 w-4" />
            Change Password
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={async () => {
            await authApi.logout().catch(console.error)
            logout()
          }}>
            <LogOutIcon className="mr-2 h-4 w-4" />
            Logout
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      
      <ChangePasswordDialog 
        open={isChangePasswordOpen} 
        onOpenChange={setIsChangePasswordOpen} 
      />
    </>
  )
}