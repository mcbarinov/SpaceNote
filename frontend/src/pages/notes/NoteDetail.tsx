import { useParams, Link } from "react-router"
import { useEffect, useState } from "react"
import { notesApi, type Note } from "../../lib/api"
import { useSpacesStore } from "@/stores/spacesStore"
import { formatFieldValue, formatDateTime } from "../../lib/formatters"
import { Button } from "@/components/ui/button"
import { NoteBreadcrumb } from "./components/NoteBreadcrumb"
import { Comments } from "./components/Comments"
import { Markdown } from "@/components/Markdown"
import { renderLiquidTemplate } from "@/lib/liquidRenderer"
import { TemplatedNoteContent } from "./components/TemplatedNoteContent"

export default function NoteDetail() {
  const { spaceId, noteId } = useParams<{ spaceId: string; noteId: string }>()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const [note, setNote] = useState<Note | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [renderedTemplate, setRenderedTemplate] = useState<string | null>(null)

  useEffect(() => {
    if (!spaceId || !noteId || !space) return

    const loadNote = async () => {
      try {
        setLoading(true)
        setError(null)
        const noteData = await notesApi.getNote(spaceId, Number(noteId))
        setNote(noteData)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load note")
      } finally {
        setLoading(false)
      }
    }

    loadNote()
  }, [spaceId, noteId, space])

  useEffect(() => {
    if (!note || !space || !space.note_detail_template) {
      setRenderedTemplate(null)
      return
    }

    const renderTemplate = async () => {
      try {
        const rendered = await renderLiquidTemplate(space.note_detail_template, { note, space })
        setRenderedTemplate(rendered)
      } catch (err) {
        console.error("Template rendering failed:", err)
        setRenderedTemplate(null)
      }
    }

    renderTemplate()
  }, [note, space])

  if (loading) {
    return <div className="mt-4">Loading...</div>
  }

  if (error) {
    return <div className="mt-4 text-red-600">Error: {error}</div>
  }

  if (!note || !space) {
    return <div className="mt-4">Note not found</div>
  }

  return (
    <div>
      <NoteBreadcrumb spaceId={spaceId!} spaceName={space.name} currentPage={`Note #${note.id}`} showNoteAsLink={false} />

      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Note #{note.id}</h1>
        <Button asChild>
          <Link to={`/notes/${spaceId}/${noteId}/edit`}>Edit</Link>
        </Button>
      </div>

      {renderedTemplate ? (
        <div className="bg-white border border-gray-300 rounded-lg p-6 mt-4">
          <TemplatedNoteContent content={renderedTemplate} />
        </div>
      ) : (
        <div className="bg-white border border-gray-300 rounded-lg p-6 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-gray-600">Author:</span>
              <span className="ml-2">{note.author}</span>
            </div>
            <div>
              <span className="text-gray-600">Created:</span>
              <span className="ml-2">{formatDateTime(note.created_at)}</span>
            </div>
            {note.edited_at && (
              <div>
                <span className="text-gray-600">Edited:</span>
                <span className="ml-2">{formatDateTime(note.edited_at)}</span>
              </div>
            )}
            {note.comment_count > 0 && (
              <div>
                <span className="text-gray-600">Comments:</span>
                <span className="ml-2">{note.comment_count}</span>
              </div>
            )}
          </div>

          <div className="mt-6 space-y-4">
            {space.fields.map(field => {
              const value = note.fields[field.name]

              return (
                <div key={field.name}>
                  <h3 className="font-semibold text-gray-700 mb-1">{field.name}</h3>
                  <div className="text-gray-900">
                    {field.type === "markdown" ? <Markdown content={String(value || "")} /> : <p>{formatFieldValue(value)}</p>}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="mt-8 bg-white border border-gray-300 rounded-lg p-6">
        <Comments spaceId={spaceId!} noteId={Number(noteId)} />
      </div>
    </div>
  )
}
