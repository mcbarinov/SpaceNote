import { useParams, useSearchParams, Link } from "react-router"
import { useEffect, useState } from "react"
import { notesApi, type Filter, type PaginationResult } from "../../lib/api"
import { NotesTable } from "./components/NotesTable"
import { FilterDropdown } from "./components/FilterDropdown"
import { PaginationControls } from "./components/PaginationControls"
import { useSpacesStore } from "@/stores/spacesStore"
import { Button } from "@/components/ui/button"

export default function SpaceNotes() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const [notesData, setNotesData] = useState<PaginationResult | null>(null)
  const [selectedFilter, setSelectedFilter] = useState<Filter | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const currentPage = parseInt(searchParams.get("page") || "1", 10)

  useEffect(() => {
    if (!spaceId || !space) return

    const loadNotes = async () => {
      try {
        setLoading(true)
        setError(null)

        // Load notes only - space data comes from cache
        const notesResponse = await notesApi.listNotes(spaceId, {
          filterId: selectedFilter?.id,
          page: currentPage,
        })
        setNotesData(notesResponse)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load notes")
      } finally {
        setLoading(false)
      }
    }

    loadNotes()
  }, [spaceId, selectedFilter, currentPage, space])

  const handleFilterSelect = async (filter: Filter | null) => {
    if (!spaceId) return

    setSelectedFilter(filter)
    // Reset to page 1 when changing filters
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      newParams.delete("page")
      return newParams
    })
  }

  const handlePageChange = (page: number) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      if (page === 1) {
        newParams.delete("page")
      } else {
        newParams.set("page", page.toString())
      }
      return newParams
    })
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
        <div className="flex items-center gap-3">
          <Button asChild>
            <Link to={`/notes/${spaceId}/new`}>New Note</Link>
          </Button>
          <FilterDropdown filters={space.filters} selectedFilter={selectedFilter} onFilterSelect={handleFilterSelect} />
        </div>
      </div>

      <div className="text-sm text-gray-600 mb-4">
        Showing {(currentPage - 1) * notesData.page_size + 1}-{Math.min(currentPage * notesData.page_size, notesData.total_count)}{" "}
        of {notesData.total_count} notes
      </div>

      <NotesTable notes={notesData.notes} listFields={selectedFilter?.list_fields || space.list_fields} space={space} />

      <div className="mt-8">
        <PaginationControls
          currentPage={currentPage}
          totalPages={notesData.total_pages}
          hasNext={notesData.has_next}
          hasPrev={notesData.has_prev}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  )
}
