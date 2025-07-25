import { useSpacesStore } from "@/stores/spacesStore"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Check, X } from "lucide-react"
import { useDialog } from "@/lib/dialog"

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
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-4">ID</th>
                <th className="text-left p-4">Name</th>
                <th className="text-center p-4">Members</th>
                <th className="text-center p-4">Fields</th>
                <th className="text-center p-4">Filters</th>
                <th className="text-center p-4">Telegram</th>
              </tr>
            </thead>
            <tbody>
              {spaces.map(space => (
                <tr key={space.id} className="border-b hover:bg-gray-50">
                  <td className="p-4 font-mono text-sm">{space.id}</td>
                  <td className="p-4">{space.name}</td>
                  <td className="p-4 text-center">{space.members.length}</td>
                  <td className="p-4 text-center">{space.fields.length}</td>
                  <td className="p-4 text-center">{space.filters.length}</td>
                  <td className="p-4 text-center">
                    {space.telegram?.enabled ? (
                      <Check className="w-4 h-4 text-green-600 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-gray-400 mx-auto" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
