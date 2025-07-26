import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import type { BaseDialogProps } from "@/lib/dialog"
import { spacesApi } from "@/lib/api/spaces"
import { useSpacesStore } from "@/stores/spacesStore"
import { toast } from "sonner"

const formSchema = z.object({
  id: z
    .string()
    .min(1, "Space ID is required")
    .regex(/^[a-z0-9-]+$/, "Only lowercase letters, numbers, and hyphens allowed"),
  name: z.string().min(1, "Space name is required"),
})

export function CreateSpaceDialog({ onClose, onSuccess }: BaseDialogProps) {
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      id: "",
      name: "",
    },
  })

  const handleSubmit = async (data: z.infer<typeof formSchema>) => {
    await spacesApi.createSpace(data)
    await refreshSpaces()
    toast.success("Space created successfully")
    onSuccess?.("Space created successfully")
    onClose()
  }

  return (
    <Dialog open onOpenChange={() => !form.formState.isSubmitting && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Space</DialogTitle>
          <DialogDescription>Enter a unique ID and name for your new space.</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Space ID</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="my-space" disabled={form.formState.isSubmitting} />
                  </FormControl>
                  <FormDescription>Only lowercase letters, numbers, and hyphens</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Space Name</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="My Space" disabled={form.formState.isSubmitting} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose} disabled={form.formState.isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {form.formState.isSubmitting ? "Creating..." : "Create Space"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default CreateSpaceDialog
