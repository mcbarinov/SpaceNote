import { useState, useCallback, Suspense } from "react"
import { DialogContext } from "./DialogContext"
import { dialogRegistry } from "./registry"
import type { DialogState, DialogContextType } from "./types"

interface DialogProviderProps {
  children: React.ReactNode
}

export function DialogProvider({ children }: DialogProviderProps) {
  // State to hold all currently open dialogs
  const [dialogs, setDialogs] = useState<DialogState[]>([])

  // Function to open a dialog
  const openDialog = useCallback((id: string, props: Record<string, unknown> = {}) => {
    return new Promise((resolve, reject) => {
      // Get component from registry
      const component = dialogRegistry[id as keyof typeof dialogRegistry]
      if (!component) {
        reject(new Error(`Dialog "${id}" not found in registry`))
        return
      }

      // Create dialog state
      const dialogState: DialogState = {
        id,
        component,
        props,
        resolve,
      }

      // Add to dialogs array
      setDialogs(prev => [...prev, dialogState])
    })
  }, [])

  // Function to close specific dialog
  const closeDialog = useCallback((id: string, result?: unknown) => {
    setDialogs(prev => {
      const dialogIndex = prev.findIndex(d => d.id === id)
      if (dialogIndex === -1) return prev

      const dialog = prev[dialogIndex]

      // Resolve the promise if it exists
      if (dialog.resolve) {
        dialog.resolve(result)
      }

      // Remove dialog from array
      return prev.filter((_, index) => index !== dialogIndex)
    })
  }, [])

  // Function to close all dialogs
  const closeAllDialogs = useCallback(() => {
    setDialogs(prev => {
      // Resolve all promises
      prev.forEach(dialog => {
        if (dialog.resolve) {
          dialog.resolve(undefined)
        }
      })
      return []
    })
  }, [])

  // Create context value
  const contextValue: DialogContextType = {
    dialogs,
    openDialog,
    closeDialog,
    closeAllDialogs,
  }

  return (
    <DialogContext.Provider value={contextValue}>
      {children}

      {/* Render all open dialogs */}
      {dialogs.map(({ id, component: Component, props }) => (
        <Suspense key={id} fallback={<div>Loading dialog...</div>}>
          <Component {...props} onClose={() => closeDialog(id)} onSuccess={result => closeDialog(id, result)} />
        </Suspense>
      ))}
    </DialogContext.Provider>
  )
}
