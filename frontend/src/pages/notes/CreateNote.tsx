import { useParams, useNavigate, Link } from "react-router"
import { useState } from "react"
import { useSpacesStore } from "@/stores/spacesStore"
import { notesApi, type CreateNoteRequest } from "@/lib/api/notes"
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb"
import { NoteForm } from "./components/NoteForm"

export default function CreateNote() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const navigate = useNavigate()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (fields: Record<string, string>) => {
    if (!spaceId) return

    try {
      setLoading(true)
      setError(null)

      const request: CreateNoteRequest = { fields }
      const createdNote = await notesApi.createNote(spaceId, request)

      // Navigate to the created note
      navigate(`/notes/${spaceId}/${createdNote.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create note")
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate(`/notes/${spaceId}`)
  }

  if (!space) {
    return <div className="mt-4">Loading...</div>
  }

  return (
    <div>
      <Breadcrumb className="my-4">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to={`/notes/${spaceId}`}>Notes / {space.name}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>New Note</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <h1 className="text-2xl font-bold my-4">Create New Note</h1>

      {error && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-4">{error}</div>}

      <div className="bg-white border border-gray-300 rounded-lg p-6">
        <NoteForm space={space} onSubmit={handleSubmit} onCancel={handleCancel} loading={loading} />
      </div>
    </div>
  )
}
