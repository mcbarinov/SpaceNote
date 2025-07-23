import path from "path"
import { defineConfig, loadEnv } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "SPACENOTE_")

  return {
    plugins: [react(), tailwindcss()],
    resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
    server: {
      port: parseInt(env.SPACENOTE_FRONTEND_PORT) || 3002,
    },
    define: {
      __SPACENOTE_API_BASE_URL__: JSON.stringify(env.SPACENOTE_API_BASE_URL || "http://localhost:3000"),
      __SPACENOTE_WS_URL__: JSON.stringify(env.SPACENOTE_WS_URL || "ws://localhost:3000"),
    },
  }
})
