import { useState, useEffect } from "react"
import type { FormEvent } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { BaseDialogProps } from "@/lib/dialog"
import { usersApi } from "@/lib/api/users"

interface User {
  id: string
}

export function UserManagementDialog({ onClose }: BaseDialogProps) {
  const [users, setUsers] = useState<User[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string>()

  const loadUsers = async () => {
    try {
      const userList = await usersApi.getUsers()
      setUsers(userList)
    } catch {
      setError("Failed to load users")
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    const formData = new FormData(e.currentTarget)
    const username = (formData.get("username") as string).trim()
    const password = formData.get("password") as string

    if (!username || !password) return

    setIsSubmitting(true)
    setError(undefined)

    try {
      await usersApi.createUser({ username, password })
      await loadUsers()
      e.currentTarget.reset()
    } catch {
      setError("Failed to create user")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open onOpenChange={() => onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Manage Users</DialogTitle>
          <DialogDescription>View and create system users.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {error && <p className="text-sm text-red-600">{error}</p>}
          
          <div className="border rounded-md divide-y">
            {users.map(user => (
              <div key={user.id} className="px-4 py-2">
                <span className="text-sm">{user.id}</span>
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 border-t pt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Username"
                  disabled={isSubmitting}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Password"
                  disabled={isSubmitting}
                />
              </div>
            </div>
            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Creating..." : "Create User"}
            </Button>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default UserManagementDialog