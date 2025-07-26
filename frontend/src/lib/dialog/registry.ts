import ChangePasswordDialog from "../../dialogs/ChangePasswordDialog"
import UserManagementDialog from "../../dialogs/UserManagementDialog"
import CreateSpaceDialog from "../../dialogs/CreateSpaceDialog"
import ImportSpaceDialog from "../../dialogs/ImportSpaceDialog"

// Registry maps dialog IDs to their components
export const dialogRegistry = {
  changePassword: ChangePasswordDialog,
  userManagement: UserManagementDialog,
  createSpace: CreateSpaceDialog,
  importSpace: ImportSpaceDialog,
} as const

// Extract dialog IDs as a union type for TypeScript
export type DialogId = keyof typeof dialogRegistry
