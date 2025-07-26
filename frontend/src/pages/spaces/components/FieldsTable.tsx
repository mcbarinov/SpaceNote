import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
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
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Required</TableHead>
              <TableHead>Options</TableHead>
              <TableHead>Default</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.map(field => (
              <TableRow key={field.name}>
                <TableCell className="font-medium">{field.name}</TableCell>
                <TableCell>{formatFieldType(field.type)}</TableCell>
                <TableCell>
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      field.required ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-800"
                    }`}>
                    {field.required ? "Required" : "Optional"}
                  </span>
                </TableCell>
                <TableCell className="text-muted-foreground">{formatOptions(field)}</TableCell>
                <TableCell className="text-muted-foreground">{formatDefault(field)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
