import { useState } from "react"
import type { FormEvent } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { BaseDialogProps } from "@/lib/dialog"
import { spacesApi } from "@/lib/api/spaces"
import { useSpacesStore } from "@/stores/spacesStore"
import { toast } from "sonner"

export function CreateSpaceDialog({ onClose, onSuccess }: BaseDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    const formData = new FormData(e.currentTarget)
    const id = formData.get("id") as string
    const name = formData.get("name") as string

    setIsSubmitting(true)
    await spacesApi.createSpace({ id, name })
    await refreshSpaces()
    toast.success("Space created successfully")
    onSuccess?.("Space created successfully")
    onClose()
    setIsSubmitting(false)
  }

  return (
    <Dialog open onOpenChange={() => !isSubmitting && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Space</DialogTitle>
          <DialogDescription>Enter a unique ID and name for your new space.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="id">Space ID</Label>
            <Input
              id="id"
              name="id"
              type="text"
              placeholder="my-space"
              pattern="[a-z0-9-]+"
              title="Only lowercase letters, numbers, and hyphens"
              required
              disabled={isSubmitting}
            />
            <p className="text-xs text-gray-500">Only lowercase letters, numbers, and hyphens</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Space Name</Label>
            <Input id="name" name="name" type="text" placeholder="My Space" required disabled={isSubmitting} />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Space"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default CreateSpaceDialog
