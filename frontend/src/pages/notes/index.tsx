import { Link } from "react-router"

const mockSpaces = [
  { id: "my-tasks", name: "My Tasks" },
  { id: "work-notes", name: "Work Notes" },
  { id: "personal-journal", name: "Personal Journal" },
]

export default function NotesIndexPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">My Spaces</h1>
      <ul className="space-y-4">
        {mockSpaces.map((space) => (
          <li key={space.id}>
            <Link to={`/notes/${space.id}`} className="hover:underline">
              {space.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
