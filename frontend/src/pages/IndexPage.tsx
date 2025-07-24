import { useEffect } from "react"
import { useNavigate } from "react-router"
import { useSpacesStore } from "@/stores/spacesStore"

export default function IndexPage() {
  const navigate = useNavigate()
  const { spaces, isLoading, error, loadSpaces } = useSpacesStore()

  useEffect(() => {
    loadSpaces()
  }, [loadSpaces])

  useEffect(() => {
    if (!isLoading && spaces.length > 0) {
      navigate(`/notes/${spaces[0].id}`, { replace: true })
    }
  }, [isLoading, spaces, navigate])

  if (isLoading) return <div>Loading your spaces...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div className="text-center max-w-md mx-auto mt-20">
      <h1 className="text-2xl font-bold mb-4">Welcome to SpaceNote!</h1>
      <p className="text-gray-600 mb-6">You don't have any spaces yet. Contact your administrator to create your first space.</p>
    </div>
  )
}
