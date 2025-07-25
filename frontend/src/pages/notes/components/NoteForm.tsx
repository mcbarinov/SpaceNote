import { useForm, type UseFormRegister, type UseFormSetValue, type FieldError, type Resolver } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Space, SpaceField } from "@/lib/api/spaces"

interface NoteFormProps {
  space: Space
  onSubmit: (fields: Record<string, string>) => void
  onCancel: () => void
  loading: boolean
  initialValues?: Record<string, unknown>
  mode?: "create" | "edit"
}

interface FieldWrapperProps {
  field: SpaceField
  error?: FieldError
  children: React.ReactNode
  helpText?: string
}

const FieldWrapper = ({ field, error, children, helpText }: FieldWrapperProps) => (
  <div key={field.name} className="space-y-2">
    <Label htmlFor={field.name}>
      {field.name}
      {field.required && <span className="text-red-500 ml-1">*</span>}
    </Label>
    {children}
    {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
    {error && <p className="text-sm text-red-500">{error.message}</p>}
  </div>
)

const getInputComponent = (
  field: SpaceField,
  space: Space,
  register: UseFormRegister<Record<string, string>>,
  setValue: UseFormSetValue<Record<string, string>>,
  error: FieldError | undefined,
  defaultValue: string
) => {
  const commonProps = {
    id: field.name,
    className: error ? "border-red-500" : "",
  }

  switch (field.type) {
    case "markdown":
      return <Textarea {...commonProps} {...register(field.name)} rows={6} placeholder="You can use markdown formatting..." />

    case "boolean":
      return (
        <Checkbox
          {...commonProps}
          onCheckedChange={checked => setValue(field.name, String(Boolean(checked)))}
          defaultChecked={defaultValue === "true"}
        />
      )

    case "choice": {
      const choices = (field.options.values as string[]) || []
      return (
        <Select onValueChange={value => setValue(field.name, value)} defaultValue={defaultValue}>
          <SelectTrigger className={error ? "border-red-500" : ""}>
            <SelectValue placeholder="Select an option..." />
          </SelectTrigger>
          <SelectContent>
            {choices.map(choice => (
              <SelectItem key={choice} value={choice}>
                {choice}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )
    }

    case "user":
      return (
        <Select onValueChange={value => setValue(field.name, value)} defaultValue={defaultValue}>
          <SelectTrigger className={error ? "border-red-500" : ""}>
            <SelectValue placeholder="Select a user..." />
          </SelectTrigger>
          <SelectContent>
            {space.members.map(member => (
              <SelectItem key={member} value={member}>
                {member}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )

    default: {
      // string, tags, datetime, int, float, image
      const inputType =
        field.type === "datetime" ? "datetime-local" : field.type === "int" || field.type === "float" ? "number" : "text"
      const step = field.type === "int" ? "1" : field.type === "float" ? "0.01" : undefined
      const placeholder =
        field.type === "tags"
          ? "Enter tags separated by commas..."
          : field.type === "image"
            ? "Image attachment ID or leave empty..."
            : undefined

      return (
        <Input
          {...commonProps}
          {...register(field.name)}
          type={inputType}
          step={step}
          min={field.options.min as number}
          max={field.options.max as number}
          placeholder={placeholder}
        />
      )
    }
  }
}

export function NoteForm({ space, onSubmit, onCancel, loading, initialValues = {}, mode = "create" }: NoteFormProps) {
  // Filter out hidden fields from create form (only for create mode)
  const visibleFields =
    mode === "create" ? space.fields.filter(field => !space.hidden_create_fields.includes(field.name)) : space.fields

  // Create dynamic schema based on space fields
  const createSchema = () => {
    const schemaFields: Record<string, z.ZodTypeAny> = {}

    visibleFields.forEach(field => {
      let fieldSchema: z.ZodTypeAny = z.string()

      if (field.type === "boolean") {
        fieldSchema = z.boolean().transform(val => val.toString())
      } else if (field.type === "int" || field.type === "float") {
        fieldSchema = z.string().min(1, `${field.name} is required`)
      } else if (field.type === "tags") {
        fieldSchema = z.string().transform(val => val) // Tags as comma-separated string
      } else {
        fieldSchema = z.string()
      }

      if (field.required && field.type !== "boolean") {
        if (field.type === "int" || field.type === "float") {
          // Already handled above
        } else {
          fieldSchema = (fieldSchema as z.ZodString).min(1, `${field.name} is required`)
        }
      } else if (!field.required) {
        fieldSchema = fieldSchema.optional().or(z.literal(""))
      }

      schemaFields[field.name] = fieldSchema
    })

    return z.object(schemaFields)
  }

  const schema = createSchema()
  type FormData = Record<string, string>

  const getDefaultValue = (field: SpaceField): string => {
    if (initialValues && field.name in initialValues) {
      const value = initialValues[field.name]
      return value ? String(value) : ""
    }
    return field.default ? String(field.default) : ""
  }

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<FormData>({
    resolver: zodResolver(schema) as Resolver<FormData>,
    defaultValues: Object.fromEntries(visibleFields.map(field => [field.name, getDefaultValue(field)])),
  })

  const onFormSubmit = (data: FormData) => {
    // Convert form data to strings for API
    const fields: Record<string, string> = {}
    visibleFields.forEach(field => {
      const value = data[field.name as keyof FormData]
      fields[field.name] = value ? String(value) : ""
    })
    onSubmit(fields)
  }

  const renderField = (field: SpaceField) => {
    const error = errors[field.name as keyof FormData] as FieldError | undefined
    const defaultValue = getDefaultValue(field)
    const helpText =
      field.type === "tags"
        ? "Separate multiple tags with commas"
        : field.type === "image"
          ? "Image attachments will be supported in a future update"
          : undefined

    return (
      <FieldWrapper key={field.name} field={field} error={error} helpText={helpText}>
        {getInputComponent(field, space, register, setValue, error, defaultValue)}
      </FieldWrapper>
    )
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      {visibleFields.map(renderField)}

      <div className="flex space-x-3 pt-4">
        <Button type="submit" disabled={loading}>
          {loading ? (mode === "edit" ? "Updating..." : "Creating...") : mode === "edit" ? "Update Note" : "Create Note"}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
