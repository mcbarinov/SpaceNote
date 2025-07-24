import { useParams, Link } from "react-router"
import { useEffect, useState } from "react"
import { notesApi, spacesApi, type Filter, type PaginationResult, type Space } from "../../lib/api"
import { NotesTable } from "../../components/NotesTable"
import { FilterDropdown } from "../../components/FilterDropdown"

export default function SpaceNotes() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const [space, setSpace] = useState<Space | null>(null)
  const [notesData, setNotesData] = useState<PaginationResult | null>(null)
  const [filters, setFilters] = useState<Filter[]>([])
  const [selectedFilter, setSelectedFilter] = useState<Filter | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!spaceId) return

    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Load space info
        const spaceResponse = await spacesApi.getSpace(spaceId)
        setSpace(spaceResponse)
        setFilters(spaceResponse.filters)

        // Load notes
        const notesResponse = await notesApi.listNotes(spaceId, {
          filterId: selectedFilter?.id,
        })
        setNotesData(notesResponse)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data")
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [spaceId, selectedFilter])

  const handleFilterSelect = async (filter: Filter | null) => {
    if (!spaceId) return

    setSelectedFilter(filter)
  }

  if (loading) {
    return (
      <div>
        <Link to="/notes" className="hover:underline">
          ← Back to spaces
        </Link>
        <div className="mt-4">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <Link to="/notes" className="hover:underline">
          ← Back to spaces
        </Link>
        <div className="mt-4 text-red-600">Error: {error}</div>
      </div>
    )
  }

  if (!space || !notesData) {
    return (
      <div>
        <Link to="/notes" className="hover:underline">
          ← Back to spaces
        </Link>
        <div className="mt-4">No data found</div>
      </div>
    )
  }

  return (
    <div>
      <Link to="/notes" className="hover:underline">
        ← Back to spaces
      </Link>

      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Notes / {space.name}</h1>
        <div className="flex items-center gap-4">
          <FilterDropdown filters={filters} selectedFilter={selectedFilter} onFilterSelect={handleFilterSelect} />
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
