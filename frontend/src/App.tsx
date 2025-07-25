import { RouterProvider } from "react-router"
import { router } from "./router"
import { DialogProvider } from "./lib/dialog"
import { Toaster } from "@/components/ui/sonner"

function App() {
  return (
    <DialogProvider>
      <RouterProvider router={router} />
      <Toaster />
    </DialogProvider>
  )
}

export default App
