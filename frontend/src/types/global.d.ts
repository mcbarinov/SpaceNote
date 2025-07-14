export {}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      readonly SPACENOTE_SPA_PORT: string
    }
  }
}
