import { useParams, useNavigate } from "react-router"
import { useEffect, useState } from "react"
import { notesApi, type Note } from "@/lib/api/notes"
import { useSpacesStore } from "@/stores/spacesStore"
import { NoteForm } from "./components/NoteForm"
import { NoteBreadcrumb } from "./components/NoteBreadcrumb"
import { toast } from "sonner"

export default function EditNote() {
  const { spaceId, noteId } = useParams<{ spaceId: string; noteId: string }>()
  const navigate = useNavigate()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const [note, setNote] = useState<Note | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!spaceId || !noteId || !space) return

    const loadNote = async () => {
      try {
        setLoading(true)
        const noteData = await notesApi.getNote(spaceId, Number(noteId))
        setNote(noteData)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to load note"
        toast.error(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    loadNote()
  }, [spaceId, noteId, space])

  const handleSubmit = async (fields: Record<string, string>) => {
    if (!spaceId || !noteId || !space) return

    try {
      setSubmitting(true)
      await notesApi.updateNote(spaceId, Number(noteId), fields)
      toast.success("Note updated successfully")
      navigate(`/notes/${spaceId}/${noteId}`)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to update note"
      toast.error(errorMessage)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    navigate(`/notes/${spaceId}/${noteId}`)
  }

  if (loading) {
    return <div className="mt-4">Loading...</div>
  }

  if (!note || !space) {
    return <div className="mt-4">Note not found</div>
  }

  return (
    <div>
      <NoteBreadcrumb spaceId={spaceId!} spaceName={space.name} noteId={note.id} currentPage="Edit" />

      <h1 className="text-2xl font-bold my-4">Edit Note #{note.id}</h1>

      <div className="bg-white border border-gray-300 rounded-lg p-6 mt-4">
        <NoteForm
          space={space}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          loading={submitting}
          initialValues={note.fields}
          mode="edit"
        />
      </div>
    </div>
  )
}
