import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { LoginForm } from "./components/LoginForm"
import { HomePage } from "./components/HomePage"
import { ProtectedRoute } from "./components/ProtectedRoute"
import { useAuthStore } from "./stores/auth"

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <LoginForm />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
