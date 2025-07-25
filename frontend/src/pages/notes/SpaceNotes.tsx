import { useParams } from "react-router"
import { useEffect, useState } from "react"
import { notesApi, type Filter, type PaginationResult } from "../../lib/api"
import { NotesTable } from "../../components/NotesTable"
import { FilterDropdown } from "../../components/FilterDropdown"
import { useSpacesStore } from "@/stores/spacesStore"

export default function SpaceNotes() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const [notesData, setNotesData] = useState<PaginationResult | null>(null)
  const [selectedFilter, setSelectedFilter] = useState<Filter | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!spaceId || !space) return

    const loadNotes = async () => {
      try {
        setLoading(true)
        setError(null)

        // Load notes only - space data comes from cache
        const notesResponse = await notesApi.listNotes(spaceId, {
          filterId: selectedFilter?.id,
        })
        setNotesData(notesResponse)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load notes")
      } finally {
        setLoading(false)
      }
    }

    loadNotes()
  }, [spaceId, selectedFilter, space])

  const handleFilterSelect = async (filter: Filter | null) => {
    if (!spaceId) return

    setSelectedFilter(filter)
  }

  if (loading) {
    return <div className="mt-4">Loading...</div>
  }

  if (error) {
    return <div className="mt-4 text-red-600">Error: {error}</div>
  }

  if (!space || !notesData) {
    return <div className="mt-4">Loading...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Notes / {space.name}</h1>
        <div className="flex items-center gap-4">
          <FilterDropdown filters={space.filters} selectedFilter={selectedFilter} onFilterSelect={handleFilterSelect} />
          <span className="text-sm text-gray-600">{notesData.total_count} per page</span>
        </div>
      </div>

      <div className="text-sm text-gray-600 mb-4">
        Showing {notesData.notes.length} of {notesData.total_count} notes
      </div>

      <NotesTable notes={notesData.notes} listFields={selectedFilter?.list_fields || space.list_fields} />
    </div>
  )
}
