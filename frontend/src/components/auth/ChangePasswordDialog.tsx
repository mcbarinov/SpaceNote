import { useState } from "react"
import { authApi } from "../../api/auth"
import { useAuthStore } from "../../stores/auth"
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogFooter,
} from "../ui/dialog"
import { Button } from "../ui/button"
import { Input } from "../ui/input"
import { Label } from "../ui/label"

type FormState = 'idle' | 'loading' | 'success' | 'error'

interface ChangePasswordDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ChangePasswordDialog({ open, onOpenChange }: ChangePasswordDialogProps) {
  const [state, setState] = useState<FormState>('idle')
  const [error, setError] = useState('')
  const { logout } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setState('loading')
    setError('')

    const formData = new FormData(e.currentTarget)
    const currentPassword = formData.get('currentPassword') as string
    const newPassword = formData.get('newPassword') as string

    if (!currentPassword || !newPassword) {
      setError('Please fill in all fields')
      setState('error')
      return
    }

    if (newPassword.length < 4) {
      setError('Password must be at least 4 characters')
      setState('error')
      return
    }

    try {
      await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      
      setState('success')
      onOpenChange(false)
      logout()
    } catch (err: any) {
      setError(err.message || "Failed to change password")
      setState('error')
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setState('idle')
      setError('')
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Change Password</DialogTitle>
          <DialogDescription>
            Enter your current password and choose a new password.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="currentPassword">Current Password</Label>
            <Input
              id="currentPassword"
              name="currentPassword"
              type="password"
              required
              disabled={state === 'loading'}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="newPassword">New Password</Label>
            <Input
              id="newPassword"
              name="newPassword"
              type="password"
              required
              minLength={4}
              disabled={state === 'loading'}
            />
          </div>
          
          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={state === 'loading'}>
              {state === 'loading' ? "Changing..." : "Change Password"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}