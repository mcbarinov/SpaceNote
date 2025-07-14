import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { LoginForm } from "./components/LoginForm"
import { AdminPage } from "./components/AdminPage"
import { NotesPage } from "./components/NotesPage"
import { SpacesPage } from "./components/SpacesPage"
import { ProfilePage } from "./components/ProfilePage"
import { ProtectedRoute } from "./components/ProtectedRoute"
import { useAuthStore } from "./stores/auth"

function RootRedirect() {
  const { user } = useAuthStore()
  const redirectPath = user?.id === "admin" ? "/admin" : "/notes"
  return <Navigate to={redirectPath} replace />
}

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={isAuthenticated ? <RootRedirect /> : <LoginForm />} />
        <Route path="/" element={<ProtectedRoute><RootRedirect /></ProtectedRoute>} />
        <Route path="/notes" element={<ProtectedRoute><NotesPage /></ProtectedRoute>} />
        <Route path="/spaces" element={<ProtectedRoute><SpacesPage /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
