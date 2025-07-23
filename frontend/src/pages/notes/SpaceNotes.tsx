import { useParams, Link } from "react-router"

const mockNotes = {
  "my-tasks": [
    { id: 1, title: "Complete project documentation" },
    { id: 2, title: "Review pull requests" },
    { id: 3, title: "Plan sprint meeting" },
  ],
  "work-notes": [
    { id: 4, title: "Meeting notes - Q1 planning" },
    { id: 5, title: "Architecture decisions" },
  ],
  "personal-journal": [
    { id: 6, title: "January reflections" },
    { id: 7, title: "Book reading notes" },
  ],
}

export default function SpaceNotes() {
  const { spaceId } = useParams()
  const notes = mockNotes[spaceId as keyof typeof mockNotes] || []

  return (
    <div>
      <Link to="/notes" className="hover:underline">← Back to spaces</Link>
      <h1 className="text-2xl font-bold my-4">Notes in {spaceId}</h1>
      <ul className="space-y-2">
        {notes.map((note) => (
          <li key={note.id}>
            <Link to={`/notes/${spaceId}/${note.id}`} className="hover:underline">
              {note.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}