import type { Note } from "../lib/api/notes"

interface NotesTableProps {
  notes: Note[]
  listFields: string[]
}

const formatFieldValue = (value: unknown): string => {
  if (value === null || value === undefined) {
    return "-"
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? `[${value.join(", ")}]` : "-"
  }
  return String(value)
}

const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleDateString()
}

export function NotesTable({ notes, listFields }: NotesTableProps) {
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
          <tr key={note.id} className="hover:bg-gray-50">
            <td className="border border-gray-300 px-4 py-2 font-medium">#{note.id}</td>
            {listFields.map(field => (
              <td key={field} className="border border-gray-300 px-4 py-2">
                {formatFieldValue(note.fields[field])}
              </td>
            ))}
            <td className="border border-gray-300 px-4 py-2">{note.author}</td>
            <td className="border border-gray-300 px-4 py-2">{formatDateTime(note.created_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
