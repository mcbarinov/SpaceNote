import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { SpaceField } from "@/lib/api/spaces"

interface FieldsTableProps {
  fields: SpaceField[]
}

export function FieldsTable({ fields }: FieldsTableProps) {
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

  return (
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
              {fields.map((field, index) => (
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
  )
}
