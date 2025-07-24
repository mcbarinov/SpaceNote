import { lazy } from "react"

// Registry maps dialog IDs to their components
// Using lazy() for code splitting - components load only when needed
export const dialogRegistry = {
  changePassword: lazy(() => import("../../dialogs/ChangePasswordDialog")),
  userManagement: lazy(() => import("../../dialogs/UserManagementDialog")),
} as const

// Extract dialog IDs as a union type for TypeScript
export type DialogId = keyof typeof dialogRegistry
