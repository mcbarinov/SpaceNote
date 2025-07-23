import { useEffect, useState } from "react"
import { Link } from "react-router"
import { spacesApi, type Space } from "../../lib/api"

export default function NotesIndexPage() {
  const [spaces, setSpaces] = useState<Space[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSpaces = async () => {
      try {
        const spaces = await spacesApi.listSpaces()
        setSpaces(spaces)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load spaces")
      } finally {
        setLoading(false)
      }
    }

    fetchSpaces()
  }, [])

  if (loading) {
    return <div>Loading spaces...</div>
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">My Spaces</h1>
      <ul className="space-y-4">
        {spaces.map(space => (
          <li key={space.id}>
            <Link to={`/notes/${space.id}`} className="hover:underline text-2xl">
              {space.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
