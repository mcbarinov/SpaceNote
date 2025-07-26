import { useSpacesStore } from "@/stores/spacesStore"
import { Card } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Check, X, MoreHorizontal, Download, Upload } from "lucide-react"
import { useDialog } from "@/lib/dialog"
import { Link } from "react-router"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { spacesApi } from "@/lib/api/spaces"
import { downloadJSON } from "@/lib/download"

export default function SpacesPage() {
  const { spaces, isLoading, error } = useSpacesStore()
  const dialog = useDialog()

  const handleExport = async (spaceId: string, includeContent: boolean) => {
    try {
      const data = await spacesApi.exportSpace(spaceId, includeContent)
      downloadJSON(data, `${spaceId}-export.json`)
    } catch (error) {
      console.error("Export failed:", error)
    }
  }

  const handleImport = () => {
    dialog.open("importSpace")
  }

  if (isLoading) return <div>Loading spaces...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Spaces</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleImport}>
            <Upload className="w-4 h-4 mr-2" />
            Import
          </Button>
          <Button onClick={() => dialog.open("createSpace")}>Create</Button>
        </div>
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
              <TableHead className="w-[50px]"></TableHead>
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
                <TableCell className="text-center">
                  <Link to={`/spaces/${space.id}/filters`} className="text-blue-600 hover:text-blue-800 hover:underline">
                    {space.filters.length}
                  </Link>
                </TableCell>
                <TableCell className="text-center">
                  {space.telegram?.enabled ? (
                    <Check className="w-4 h-4 text-green-600 mx-auto" />
                  ) : (
                    <X className="w-4 h-4 text-gray-400 mx-auto" />
                  )}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8 p-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleExport(space.id, false)}>
                        <Download className="mr-2 h-4 w-4" />
                        Export (metadata only)
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleExport(space.id, true)}>
                        <Download className="mr-2 h-4 w-4" />
                        Export with notes
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  )
}
