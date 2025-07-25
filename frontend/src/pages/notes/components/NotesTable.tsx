import { useNavigate, useParams } from "react-router"
import type { Note } from "@/lib/api/notes"
import { formatFieldValue, formatDateOnly } from "@/lib/formatters"

interface NotesTableProps {
  notes: Note[]
  listFields: string[]
}

export function NotesTable({ notes, listFields }: NotesTableProps) {
  const navigate = useNavigate()
  const { spaceId } = useParams<{ spaceId: string }>()

  return (
    <table className="w-full border-collapse border border-gray-300">
      <thead>
        <tr className="bg-gray-50">
          <th className="border border-gray-300 px-4 py-2 text-left">id</th>
          {listFields.map(field => (
            <th key={field} className="border border-gray-300 px-4 py-2 text-left">
              {field}
            </th>
          ))}
          <th className="border border-gray-300 px-4 py-2 text-left">author</th>
          <th className="border border-gray-300 px-4 py-2 text-left">created</th>
        </tr>
      </thead>
      <tbody>
        {notes.map(note => (
          <tr key={note.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/notes/${spaceId}/${note.id}`)}>
            <td className="border border-gray-300 px-4 py-2 font-medium">#{note.id}</td>
            {listFields.map(field => (
              <td key={field} className="border border-gray-300 px-4 py-2">
                {formatFieldValue(note.fields[field])}
              </td>
            ))}
            <td className="border border-gray-300 px-4 py-2">{note.author}</td>
            <td className="border border-gray-300 px-4 py-2">{formatDateOnly(note.created_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
