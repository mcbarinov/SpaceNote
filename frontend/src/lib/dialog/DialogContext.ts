import { createContext } from "react"
import type { DialogContextType } from "./types"

// Create context with null as default value
// We'll provide real implementation in DialogProvider
export const DialogContext = createContext<DialogContextType | null>(null)
