/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
  readonly SPACENOTE_SPA_PORT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
