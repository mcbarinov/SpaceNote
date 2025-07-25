import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { spacesApi, type SpaceField } from "@/lib/api/spaces"
import { useSpacesStore } from "@/stores/spacesStore"

interface HiddenFieldsConfigProps {
  spaceId: string
  initialFields: string[]
  availableFields: SpaceField[]
}

export function HiddenFieldsConfig({ spaceId, initialFields, availableFields }: HiddenFieldsConfigProps) {
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)
  const [hiddenFields, setHiddenFields] = useState(initialFields.join(", "))
  const [isUpdating, setIsUpdating] = useState(false)
  const [message, setMessage] = useState("")

  const handleUpdate = async () => {
    setIsUpdating(true)
    setMessage("")

    try {
      const fieldNames = hiddenFields
        .split(",")
        .map(name => name.trim())
        .filter(name => name.length > 0)

      await spacesApi.updateHiddenCreateFields(spaceId, fieldNames)
      await refreshSpaces()
      setMessage("Hidden fields updated successfully!")
      setTimeout(() => setMessage(""), 3000)
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : "Failed to update"}`)
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Hidden Create Fields</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-gray-600">Enter field names to hide in the create form (comma-separated):</p>
        <p className="text-xs text-gray-500 mb-2">Note: Hidden fields must have default values if they are required.</p>
        <Input value={hiddenFields} onChange={e => setHiddenFields(e.target.value)} placeholder="field1, field2" />
        <p className="text-xs text-gray-500">Available fields: {availableFields.map(f => f.name).join(", ")}</p>
        {message && <p className={`text-sm ${message.startsWith("Error") ? "text-red-600" : "text-green-600"}`}>{message}</p>}
        <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={handleUpdate} disabled={isUpdating}>
          {isUpdating ? "Updating..." : "Update Hidden Fields"}
        </Button>
      </CardContent>
    </Card>
  )
}
