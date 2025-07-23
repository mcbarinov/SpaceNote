import { useParams, Link } from "react-router"

const mockNoteDetails = {
  1: {
    title: "Complete project documentation",
    content: "Need to update the README and add API documentation for the new endpoints.",
    author: "John Doe",
    created: "2025-01-15",
  },
  2: {
    title: "Review pull requests",
    content: "Review PRs #123, #124, and #125. Focus on code quality and test coverage.",
    author: "Jane Smith",
    created: "2025-01-14",
  },
  3: {
    title: "Plan sprint meeting",
    content: "Prepare agenda for next week's sprint planning. Include velocity discussion.",
    author: "John Doe",
    created: "2025-01-13",
  },
  4: {
    title: "Meeting notes - Q1 planning",
    content: "Key objectives: increase user engagement, improve performance, launch mobile app.",
    author: "Team Lead",
    created: "2025-01-10",
  },
  5: {
    title: "Architecture decisions",
    content: "Decided to use microservices for the new feature. Need to document trade-offs.",
    author: "Tech Lead",
    created: "2025-01-08",
  },
  6: {
    title: "January reflections",
    content: "This month has been productive. Learned new technologies and improved workflows.",
    author: "Me",
    created: "2025-01-20",
  },
  7: {
    title: "Book reading notes",
    content: "Currently reading 'Clean Code'. Key takeaways: naming matters, functions should be small.",
    author: "Me",
    created: "2025-01-18",
  },
}

export default function NoteDetail() {
  const { spaceId, noteId } = useParams()
  const note = mockNoteDetails[Number(noteId) as keyof typeof mockNoteDetails]

  if (!note) {
    return <div>Note not found</div>
  }

  return (
    <div>
      <Link to={`/notes/${spaceId}`} className="hover:underline">
        ← Back to notes
      </Link>
      <h1 className="text-2xl font-bold my-4">{note.title}</h1>
      <p className="text-gray-600 text-sm">
        By {note.author} on {note.created}
      </p>
      <div className="mt-8">
        <p>{note.content}</p>
      </div>
    </div>
  )
}
