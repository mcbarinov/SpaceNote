import { useParams, Link } from "react-router"
import { useSpacesStore } from "@/stores/spacesStore"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { spacesApi } from "@/lib/api/spaces"
import type { FilterCondition } from "@/lib/api/notes"
import { Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

export default function SpaceFilters() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)
  const [deletingFilter, setDeletingFilter] = useState<string | null>(null)

  if (!space || !spaceId) {
    return <div className="mt-4">Loading...</div>
  }

  const handleDeleteFilter = async (filterId: string) => {
    if (!confirm("Are you sure you want to delete this filter?")) return

    setDeletingFilter(filterId)
    try {
      await spacesApi.deleteFilter(spaceId, filterId)
      await refreshSpaces()
      toast.success("Filter deleted successfully")
    } catch (error) {
      toast.error("Failed to delete filter")
      console.error("Error deleting filter:", error)
    } finally {
      setDeletingFilter(null)
    }
  }

  const formatConditions = (conditions: FilterCondition[]) => {
    if (conditions.length === 0) return "-"

    return conditions.map(condition => `${condition.field} ${condition.operator} ${JSON.stringify(condition.value)}`).join(", ")
  }

  const formatSort = (sort: string[]) => {
    if (sort.length === 0) return "-"
    return sort.join(", ")
  }

  const formatListFields = (listFields: string[]) => {
    if (listFields.length === 0) return "-"
    return listFields.join(", ")
  }

  return (
    <div>
      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Filters / {space.name}</h1>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link to={`/spaces/${spaceId}/fields`}>Fields</Link>
          </Button>
          <Button asChild variant="outline">
            <Link to={`/spaces/${spaceId}/templates`}>Templates</Link>
          </Button>
          <Button asChild>
            <Link to={`/spaces/${spaceId}/filters/create`}>Create</Link>
          </Button>
        </div>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Conditions</TableHead>
              <TableHead>Sort</TableHead>
              <TableHead>List Fields</TableHead>
              <TableHead className="text-center">Delete</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {space.filters.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground">
                  No filters created yet
                </TableCell>
              </TableRow>
            ) : (
              space.filters.map(filter => (
                <TableRow key={filter.id}>
                  <TableCell className="font-mono text-sm">{filter.id}</TableCell>
                  <TableCell>{filter.title}</TableCell>
                  <TableCell>{filter.description || "-"}</TableCell>
                  <TableCell className="max-w-xs truncate">{formatConditions(filter.conditions)}</TableCell>
                  <TableCell>{formatSort(filter.sort)}</TableCell>
                  <TableCell>{formatListFields(filter.list_fields)}</TableCell>
                  <TableCell className="text-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteFilter(filter.id)}
                      disabled={deletingFilter === filter.id}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  )
}
