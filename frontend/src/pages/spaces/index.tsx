import { useSpacesStore } from "@/stores/spacesStore"
import { Card } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Check, X } from "lucide-react"
import { useDialog } from "@/lib/dialog"
import { Link } from "react-router"

export default function SpacesPage() {
  const { spaces, isLoading, error } = useSpacesStore()
  const dialog = useDialog()

  if (isLoading) return <div>Loading spaces...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Spaces</h1>
        <Button onClick={() => dialog.open("createSpace")}>Create</Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead className="text-center">Members</TableHead>
              <TableHead className="text-center">Fields</TableHead>
              <TableHead className="text-center">Filters</TableHead>
              <TableHead className="text-center">Telegram</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {spaces.map(space => (
              <TableRow key={space.id}>
                <TableCell className="font-mono text-sm">{space.id}</TableCell>
                <TableCell>{space.name}</TableCell>
                <TableCell className="text-center">{space.members.length}</TableCell>
                <TableCell className="text-center">
                  <Link to={`/spaces/${space.id}/fields`} className="text-blue-600 hover:text-blue-800 hover:underline">
                    {space.fields.length}
                  </Link>
                </TableCell>
                <TableCell className="text-center">{space.filters.length}</TableCell>
                <TableCell className="text-center">
                  {space.telegram?.enabled ? (
                    <Check className="w-4 h-4 text-green-600 mx-auto" />
                  ) : (
                    <X className="w-4 h-4 text-gray-400 mx-auto" />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  )
}
