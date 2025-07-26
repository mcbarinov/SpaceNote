import { useNavigate, useParams } from "react-router"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
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
    <Table>
      <TableHeader>
        <TableRow>
          {fieldsToShow.map(field => (
            <TableHead key={field}>{field}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {notes.map(note => (
          <TableRow key={note.id} className="cursor-pointer" onClick={() => navigate(`/notes/${spaceId}/${note.id}`)}>
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

              return <TableCell key={field}>{cellContent}</TableCell>
            })}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
