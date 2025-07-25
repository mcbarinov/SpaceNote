import { useNavigate, useParams } from "react-router"
import type { Note } from "@/lib/api/notes"
import { formatFieldValue, formatDateOnly } from "@/lib/formatters"

interface NotesTableProps {
  notes: Note[]
  listFields: string[]
}

function getCellValue(note: Note, field: string): string {
  if (field === "id") return `#${note.id}`
  if (field === "author") return note.author
  if (field === "created_at") return formatDateOnly(note.created_at)
  return formatFieldValue(note.fields[field])
}

export function NotesTable({ notes, listFields }: NotesTableProps) {
  const navigate = useNavigate()
  const { spaceId } = useParams<{ spaceId: string }>()

  const fieldsToShow = listFields.length === 0 ? ["id", "author", "created_at"] : listFields

  return (
    <table className="w-full border-collapse border border-gray-300">
      <thead>
        <tr className="bg-gray-50">
          {fieldsToShow.map(field => (
            <th key={field} className="border border-gray-300 px-4 py-2 text-left">
              {field}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {notes.map(note => (
          <tr key={note.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/notes/${spaceId}/${note.id}`)}>
            {fieldsToShow.map(field => (
              <td key={field} className="border border-gray-300 px-4 py-2">
                {getCellValue(note, field)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
