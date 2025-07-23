import { useActionState } from "react"
import { useNavigate } from "react-router"
import { authApi } from "../lib/api"
import { useAuthStore } from "../stores/authStore"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Card, CardContent } from "../components/ui/card"

interface LoginState {
  error?: string
}

export default function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore(state => state.login)

  async function loginAction(_prevState: LoginState, formData: FormData): Promise<LoginState> {
    const username = formData.get("username") as string
    const password = formData.get("password") as string

    if (!username || !password) {
      return { error: "Please enter username and password" }
    }

    try {
      const response = await authApi.login({ username, password })
      login(response.session_id, response.user_id)
      navigate("/")
      return {}
    } catch (_error) {
      return { error: "Invalid username or password" }
    }
  }

  const [state, formAction, isPending] = useActionState(loginAction, {})

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardContent>
          <form action={formAction} className="space-y-4">
            <Input
              id="username"
              name="username"
              type="text"
              placeholder="Enter username"
              required
              autoFocus
              disabled={isPending}
            />
            <Input id="password" name="password" type="password" placeholder="Enter password" required disabled={isPending} />
            {state.error && <p className="text-sm text-red-600">{state.error}</p>}
            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? "Logging in..." : "Login"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
