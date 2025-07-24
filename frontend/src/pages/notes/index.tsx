import { Link } from "react-router"
import { useSpacesStore } from "@/stores/spacesStore"

export default function NotesIndexPage() {
  const { spaces, isLoading, error } = useSpacesStore()

  if (isLoading) {
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
