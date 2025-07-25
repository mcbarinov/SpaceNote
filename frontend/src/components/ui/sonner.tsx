import { Toaster as Sonner } from "sonner"

const Toaster = () => {
  return (
    <Sonner
      position="top-center"
      toastOptions={{
        style: {
          background: "white",
          color: "black",
          border: "1px solid #e5e7eb",
        },
        classNames: {
          error: "!bg-red-500 !text-white !border-red-600",
          success: "!bg-green-500 !text-white !border-green-600",
          warning: "!bg-yellow-500 !text-white !border-yellow-600",
          info: "!bg-blue-500 !text-white !border-blue-600",
        },
      }}
    />
  )
}

export { Toaster }
