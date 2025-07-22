import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: parseInt(process.env["SPACENOTE_SPA_PORT"] ?? "3001"),
    host: true,
    proxy: {
      "/new-api": {
        target: `http://localhost:${process.env["SPACENOTE_PORT"] ?? "3000"}`,
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    target: "es2022",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    exclude: ["lucide-react"],
  },
})
