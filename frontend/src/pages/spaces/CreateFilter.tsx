import { useParams, useNavigate, Link } from "react-router"
import { useSpacesStore } from "@/stores/spacesStore"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { spacesApi } from "@/lib/api/spaces"
import { useState } from "react"
import { toast } from "sonner"
import { X, Plus } from "lucide-react"
import type { Filter, FilterCondition } from "@/lib/api/notes"
import type { FieldType } from "@/lib/api/spaces"

interface FilterFormData {
  id: string
  title: string
  description: string
  conditions: FilterCondition[]
  sort: string[]
  list_fields: string[]
}

const OPERATORS_BY_TYPE: Record<FieldType, string[]> = {
  string: ["eq", "ne", "contains", "startswith", "endswith", "in"],
  markdown: ["eq", "ne", "contains", "startswith", "endswith", "in"],
  boolean: ["eq", "ne"],
  choice: ["eq", "ne", "in"],
  tags: ["contains", "in", "all"],
  user: ["eq", "ne", "in"],
  datetime: ["eq", "ne", "gt", "gte", "lt", "lte"],
  int: ["eq", "ne", "gt", "gte", "lt", "lte", "in"],
  float: ["eq", "ne", "gt", "gte", "lt", "lte", "in"],
  image: ["eq", "ne"],
}

const OPERATOR_LABELS: Record<string, string> = {
  eq: "equals",
  ne: "not equals",
  gt: "greater than",
  gte: "greater than or equal",
  lt: "less than",
  lte: "less than or equal",
  contains: "contains",
  startswith: "starts with",
  endswith: "ends with",
  in: "in (has any)",
  all: "has all",
}

export default function CreateFilter() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const navigate = useNavigate()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)

  const [formData, setFormData] = useState<FilterFormData>({
    id: "",
    title: "",
    description: "",
    conditions: [],
    sort: [],
    list_fields: [],
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!space || !spaceId) {
    return <div className="mt-4">Loading...</div>
  }

  // Get all available fields (built-in + custom)
  const builtInFields = [
    { name: "id", type: "int" as FieldType },
    { name: "author", type: "user" as FieldType },
    { name: "created_at", type: "datetime" as FieldType },
  ]

  const allFields = [...builtInFields, ...space.fields.map(f => ({ name: f.name, type: f.type }))]

  const addCondition = () => {
    setFormData(prev => ({
      ...prev,
      conditions: [...prev.conditions, { field: "", operator: "", value: "" }],
    }))
  }

  const removeCondition = (index: number) => {
    setFormData(prev => ({
      ...prev,
      conditions: prev.conditions.filter((_, i) => i !== index),
    }))
  }

  const updateCondition = (index: number, updates: Partial<FilterCondition>) => {
    setFormData(prev => ({
      ...prev,
      conditions: prev.conditions.map((condition, i) => (i === index ? { ...condition, ...updates } : condition)),
    }))
  }

  const getFieldType = (fieldName: string): FieldType => {
    const field = allFields.find(f => f.name === fieldName)
    return field?.type || "string"
  }

  const getAvailableOperators = (fieldName: string): string[] => {
    const fieldType = getFieldType(fieldName)
    return OPERATORS_BY_TYPE[fieldType] || []
  }

  const parseValue = (value: string, operator: string) => {
    if (operator === "in" || operator === "all") {
      // Parse comma-separated values for array operators
      return value
        .split(",")
        .map(v => v.trim())
        .filter(v => v)
    }
    if (value === "true" || value === "false") {
      return value === "true"
    }
    if (!isNaN(Number(value)) && value !== "") {
      return Number(value)
    }
    return value
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.id.trim() || !formData.title.trim()) {
      toast.error("ID and title are required")
      return
    }

    // Validate conditions
    for (const condition of formData.conditions) {
      if (!condition.field || !condition.operator) {
        toast.error("All conditions must have a field and operator")
        return
      }
    }

    setIsSubmitting(true)
    try {
      const filter: Filter = {
        id: formData.id.trim(),
        title: formData.title.trim(),
        description: formData.description.trim(),
        conditions: formData.conditions.map(c => ({
          field: c.field,
          operator: c.operator,
          value: parseValue(c.value as string, c.operator),
        })),
        sort: formData.sort,
        list_fields: formData.list_fields,
      }

      await spacesApi.createFilter(spaceId, filter)
      await refreshSpaces()
      toast.success("Filter created successfully")
      navigate(`/spaces/${spaceId}/filters`)
    } catch (error) {
      toast.error("Failed to create filter")
      console.error("Error creating filter:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSortChange = (value: string) => {
    const sortFields = value
      .split(",")
      .map(s => s.trim())
      .filter(s => s)
    setFormData(prev => ({ ...prev, sort: sortFields }))
  }

  return (
    <div>
      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Create Filter / {space.name}</h1>
        <Button asChild variant="outline">
          <Link to={`/spaces/${spaceId}/filters`}>Back to Filters</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="id">ID (e.g. urgent-tasks)</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={e => setFormData(prev => ({ ...prev, id: e.target.value }))}
                  placeholder="urgent-tasks"
                  required
                />
              </div>
              <div>
                <Label htmlFor="title">Title (e.g. Urgent Tasks)</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={e => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Urgent Tasks"
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Filter description..."
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-4">
                <Label className="text-base font-semibold">Filter Conditions</Label>
                <Button type="button" onClick={addCondition} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Condition
                </Button>
              </div>

              {formData.conditions.map((condition, index) => (
                <div key={index} className="flex gap-2 items-end mb-2">
                  <div className="flex-1">
                    <Label>Field</Label>
                    <Select
                      value={condition.field}
                      onValueChange={value => updateCondition(index, { field: value, operator: "", value: "" })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select field..." />
                      </SelectTrigger>
                      <SelectContent>
                        {allFields.map(field => (
                          <SelectItem key={field.name} value={field.name}>
                            {field.name} ({field.type})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex-1">
                    <Label>Operator</Label>
                    <Select
                      value={condition.operator}
                      onValueChange={value => updateCondition(index, { operator: value })}
                      disabled={!condition.field}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select operator..." />
                      </SelectTrigger>
                      <SelectContent>
                        {getAvailableOperators(condition.field).map(op => (
                          <SelectItem key={op} value={op}>
                            {OPERATOR_LABELS[op]}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex-1">
                    <Label>Value</Label>
                    <Input
                      value={condition.value as string}
                      onChange={e => updateCondition(index, { value: e.target.value })}
                      placeholder={condition.operator === "in" || condition.operator === "all" ? "value1, value2" : "value"}
                    />
                  </div>

                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeCondition(index)}
                    className="text-red-600 hover:text-red-700">
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ))}

              {formData.conditions.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No conditions added yet. Click "Add Condition" to add filter criteria.
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="sort">Sort fields (comma-separated, use - for descending)</Label>
              <Input
                id="sort"
                value={formData.sort.join(", ")}
                onChange={e => handleSortChange(e.target.value)}
                placeholder="-created_at, priority"
              />
              <p className="text-sm text-muted-foreground mt-1">Example: -created_at, priority</p>
            </div>

            <div>
              <Label htmlFor="list_fields">Additional list fields (comma-separated)</Label>
              <Input
                id="list_fields"
                value={formData.list_fields.join(", ")}
                onChange={e => {
                  const fields = e.target.value
                    .split(",")
                    .map(f => f.trim())
                    .filter(f => f)
                  setFormData(prev => ({ ...prev, list_fields: fields }))
                }}
                placeholder="title, status, priority, assignee"
              />
              <p className="text-sm text-muted-foreground mt-1">Available fields: {allFields.map(f => f.name).join(", ")}</p>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Filter"}
              </Button>
              <Button type="button" variant="outline" asChild>
                <Link to={`/spaces/${spaceId}/filters`}>Cancel</Link>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
