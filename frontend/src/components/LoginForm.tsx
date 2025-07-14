import { useState } from "react"
import { authApi } from "../api/auth"
import { useAuthStore } from "../stores/auth"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Card } from "./ui/card"

export function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const { login } = useAuthStore()

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    const formData = new FormData(e.currentTarget)
    const username = formData.get("username") as string
    const password = formData.get("password") as string

    try {
      const response = await authApi.login({ username, password })
      login(response.session_id, response.user)
    } catch {
      setError("Invalid username or password")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-6">
        <h1 className="text-2xl font-semibold text-center mb-6">Sign in to SpaceNote</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <Input name="username" placeholder="Username" autoComplete="username" required />
          <Input name="password" type="password" placeholder="Password" autoComplete="current-password" required />
          {error && <p className="text-sm text-red-600 text-center">{error}</p>}
          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      </Card>
    </div>
  )
}
