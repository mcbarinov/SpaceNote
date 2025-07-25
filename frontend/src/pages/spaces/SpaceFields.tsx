import { useParams } from "react-router"
import { useState } from "react"
import { useSpacesStore } from "@/stores/spacesStore"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { spacesApi, type SpaceField } from "@/lib/api/spaces"

export default function SpaceFields() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)

  const [listFields, setListFields] = useState("")
  const [hiddenFields, setHiddenFields] = useState("")
  const [isUpdatingList, setIsUpdatingList] = useState(false)
  const [isUpdatingHidden, setIsUpdatingHidden] = useState(false)
  const [listMessage, setListMessage] = useState("")
  const [hiddenMessage, setHiddenMessage] = useState("")

  if (!space) {
    return <div className="mt-4">Loading...</div>
  }

  if (listFields === "" && hiddenFields === "") {
    setListFields(space.list_fields.join(", "))
    setHiddenFields(space.hidden_create_fields.join(", "))
  }

  const formatFieldType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  const formatDefault = (field: SpaceField) => {
    if (field.default === null || field.default === undefined) {
      return "-"
    }
    if (Array.isArray(field.default)) {
      return field.default.join(", ")
    }
    if (typeof field.default === "boolean") {
      return field.default ? "Yes" : "No"
    }
    return String(field.default)
  }

  const formatOptions = (field: SpaceField) => {
    if (!field.options || Object.keys(field.options).length === 0) {
      return "-"
    }

    const optionParts: string[] = []

    Object.entries(field.options).forEach(([key, value]) => {
      if (key === "values" && Array.isArray(value)) {
        optionParts.push(`values: [${value.map(v => `'${v}'`).join(", ")}]`)
      } else if (key === "min" || key === "max") {
        optionParts.push(`${key}: ${value}`)
      }
    })

    return optionParts.join(", ") || "-"
  }

  const handleUpdateListFields = async () => {
    if (!spaceId) return

    setIsUpdatingList(true)
    setListMessage("")

    try {
      const fieldNames = listFields
        .split(",")
        .map(name => name.trim())
        .filter(name => name.length > 0)

      await spacesApi.updateListFields(spaceId, fieldNames)
      await refreshSpaces()
      setListMessage("List fields updated successfully!")
      setTimeout(() => setListMessage(""), 3000)
    } catch (error) {
      setListMessage(`Error: ${error instanceof Error ? error.message : "Failed to update"}`)
    } finally {
      setIsUpdatingList(false)
    }
  }

  const handleUpdateHiddenFields = async () => {
    if (!spaceId) return

    setIsUpdatingHidden(true)
    setHiddenMessage("")

    try {
      const fieldNames = hiddenFields
        .split(",")
        .map(name => name.trim())
        .filter(name => name.length > 0)

      await spacesApi.updateHiddenCreateFields(spaceId, fieldNames)
      await refreshSpaces()
      setHiddenMessage("Hidden fields updated successfully!")
      setTimeout(() => setHiddenMessage(""), 3000)
    } catch (error) {
      setHiddenMessage(`Error: ${error instanceof Error ? error.message : "Failed to update"}`)
    } finally {
      setIsUpdatingHidden(false)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Fields / {space.name}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Space Fields</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">Name</th>
                  <th className="text-left py-2 px-4">Type</th>
                  <th className="text-left py-2 px-4">Required</th>
                  <th className="text-left py-2 px-4">Options</th>
                  <th className="text-left py-2 px-4">Default</th>
                </tr>
              </thead>
              <tbody>
                {space.fields.map((field, index) => (
                  <tr key={field.name} className={index % 2 === 0 ? "bg-gray-50" : ""}>
                    <td className="py-2 px-4 font-medium">{field.name}</td>
                    <td className="py-2 px-4">{formatFieldType(field.type)}</td>
                    <td className="py-2 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          field.required ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-800"
                        }`}>
                        {field.required ? "Required" : "Optional"}
                      </span>
                    </td>
                    <td className="py-2 px-4 text-gray-600">{formatOptions(field)}</td>
                    <td className="py-2 px-4 text-gray-600">{formatDefault(field)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8 space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>List Fields</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">Enter field names to show in the notes list (comma-separated, order matters):</p>
            <Input value={listFields} onChange={e => setListFields(e.target.value)} placeholder="field1, field2, field3" />
            <p className="text-xs text-gray-500">Available fields: {space.fields.map(f => f.name).join(", ")}</p>
            {listMessage && (
              <p className={`text-sm ${listMessage.startsWith("Error") ? "text-red-600" : "text-green-600"}`}>{listMessage}</p>
            )}
            <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={handleUpdateListFields} disabled={isUpdatingList}>
              {isUpdatingList ? "Updating..." : "Update List Fields"}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Hidden Create Fields</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">Enter field names to hide in the create form (comma-separated):</p>
            <p className="text-xs text-gray-500 mb-2">Note: Hidden fields must have default values if they are required.</p>
            <Input value={hiddenFields} onChange={e => setHiddenFields(e.target.value)} placeholder="field1, field2" />
            <p className="text-xs text-gray-500">Available fields: {space.fields.map(f => f.name).join(", ")}</p>
            {hiddenMessage && (
              <p className={`text-sm ${hiddenMessage.startsWith("Error") ? "text-red-600" : "text-green-600"}`}>
                {hiddenMessage}
              </p>
            )}
            <Button
              className="w-full bg-blue-600 hover:bg-blue-700"
              onClick={handleUpdateHiddenFields}
              disabled={isUpdatingHidden}>
              {isUpdatingHidden ? "Updating..." : "Update Hidden Fields"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
