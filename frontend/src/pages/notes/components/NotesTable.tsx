import { useNavigate, useParams } from "react-router"
import type { Note } from "@/lib/api/notes"
import type { Space } from "@/lib/api/spaces"
import { formatFieldValue, formatDateOnly } from "@/lib/formatters"
import { Markdown } from "@/components/Markdown"

interface NotesTableProps {
  notes: Note[]
  listFields: string[]
  space: Space
}

export function NotesTable({ notes, listFields, space }: NotesTableProps) {
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
            {fieldsToShow.map(field => {
              const fieldDef = space.fields.find(f => f.name === field)
              let cellContent

              if (field === "id") {
                cellContent = `#${note.id}`
              } else if (field === "author") {
                cellContent = note.author
              } else if (field === "created_at") {
                cellContent = formatDateOnly(note.created_at)
              } else if (fieldDef?.type === "markdown") {
                cellContent = <Markdown content={String(note.fields[field] || "")} />
              } else {
                cellContent = formatFieldValue(note.fields[field])
              }

              return (
                <td key={field} className="border border-gray-300 px-4 py-2">
                  {cellContent}
                </td>
              )
            })}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
