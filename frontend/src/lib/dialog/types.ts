import type { ComponentType } from "react"

// Base props that every dialog component will receive
export interface BaseDialogProps {
  onClose: () => void
  onSuccess?: (result?: unknown) => void
}

// State of a single open dialog
export interface DialogState {
  id: string // unique identifier like 'changePassword'
  component: ComponentType<BaseDialogProps> // React component to render
  props: Record<string, unknown> // props to pass to component
  resolve?: (value: unknown) => void // Promise resolve function
  reject?: (error: Error) => void // Promise reject function
}

// Context interface - what our provider will expose
export interface DialogContextType {
  dialogs: DialogState[] // array of currently open dialogs
  openDialog: (id: string, props?: Record<string, unknown>) => Promise<unknown>
  closeDialog: (id: string, result?: unknown) => void
  closeAllDialogs: () => void
}
