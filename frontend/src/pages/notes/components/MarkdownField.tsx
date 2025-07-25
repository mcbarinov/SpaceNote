import { type UseFormRegister, type FieldError, type UseFormWatch } from "react-hook-form"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Markdown } from "@/components/Markdown"

interface MarkdownFieldProps {
  fieldName: string
  register: UseFormRegister<Record<string, string>>
  watch: UseFormWatch<Record<string, string>>
  error?: FieldError
}

export function MarkdownField({ fieldName, register, watch, error }: MarkdownFieldProps) {
  const watchedValue = watch(fieldName) || ""

  return (
    <Tabs defaultValue="write" className="w-full">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="write">Write</TabsTrigger>
        <TabsTrigger value="preview">Preview</TabsTrigger>
      </TabsList>

      <TabsContent value="write" className="mt-2">
        <Textarea
          {...register(fieldName)}
          rows={6}
          placeholder="You can use markdown formatting..."
          className={error ? "border-red-500" : ""}
        />
      </TabsContent>

      <TabsContent value="preview" className="mt-2">
        <div className="min-h-[150px] p-3 border rounded-md bg-gray-50">
          {watchedValue.trim() ? (
            <Markdown content={watchedValue} />
          ) : (
            <p className="text-gray-500 italic">Nothing to preview yet. Write some markdown in the Write tab.</p>
          )}
        </div>
      </TabsContent>
    </Tabs>
  )
}
