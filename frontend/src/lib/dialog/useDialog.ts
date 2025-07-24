import { useContext } from "react"
import { DialogContext } from "./DialogContext"
import type { DialogId } from "./registry"

// Custom hook to access dialog system
export function useDialog() {
  const context = useContext(DialogContext)

  // Ensure hook is used within DialogProvider
  if (!context) {
    throw new Error("useDialog must be used within DialogProvider")
  }

  return {
    // Open a dialog by ID with optional props
    open: <TResult = unknown>(dialogId: DialogId, props?: Record<string, unknown>): Promise<TResult> => {
      return context.openDialog(dialogId, props) as Promise<TResult>
    },

    // Close specific dialog with optional result
    close: (dialogId: string, result?: unknown) => {
      context.closeDialog(dialogId, result)
    },

    // Close all open dialogs
    closeAll: () => {
      context.closeAllDialogs()
    },

    // Get list of currently open dialogs (for debugging)
    openDialogs: context.dialogs.map(d => d.id),
  }
}
