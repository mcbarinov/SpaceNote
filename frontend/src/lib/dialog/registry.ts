import ChangePasswordDialog from "../../dialogs/ChangePasswordDialog"
import UserManagementDialog from "../../dialogs/UserManagementDialog"
import CreateSpaceDialog from "../../dialogs/CreateSpaceDialog"

// Registry maps dialog IDs to their components
export const dialogRegistry = {
  changePassword: ChangePasswordDialog,
  userManagement: UserManagementDialog,
  createSpace: CreateSpaceDialog,
} as const

// Extract dialog IDs as a union type for TypeScript
export type DialogId = keyof typeof dialogRegistry
