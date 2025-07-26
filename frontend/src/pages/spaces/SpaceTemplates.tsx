import { useParams, Link } from "react-router"
import { useState, useEffect } from "react"
import { useSpacesStore } from "@/stores/spacesStore"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { NoteBreadcrumb } from "@/pages/notes/components/NoteBreadcrumb"
import { toast } from "sonner"
import { spacesApi } from "@/lib/api/spaces"
import { validateLiquidTemplate } from "@/lib/liquidRenderer"

export default function SpaceTemplates() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))
  const refreshSpaces = useSpacesStore(state => state.refreshSpaces)

  const [noteDetailTemplate, setNoteDetailTemplate] = useState("")
  const [noteListTemplate, setNoteListTemplate] = useState("")
  const [savingDetail, setSavingDetail] = useState(false)
  const [savingList, setSavingList] = useState(false)
  useEffect(() => {
    if (space) {
      setNoteDetailTemplate(space.note_detail_template || "")
      setNoteListTemplate(space.note_list_template || "")
    }
  }, [space])

  if (!space) {
    return <div className="mt-4">Space not found</div>
  }

  const validateAllTemplates = () => {
    const detailValidation = validateLiquidTemplate(noteDetailTemplate)
    const listValidation = validateLiquidTemplate(noteListTemplate)

    if (!detailValidation.valid) {
      toast.error(`Detail template error: ${detailValidation.error}`)
      return false
    }

    if (!listValidation.valid) {
      toast.error(`List template error: ${listValidation.error}`)
      return false
    }

    toast.success("All templates are valid")
    return true
  }

  const handleSaveDetailTemplate = async () => {
    if (!spaceId) return

    const validation = validateLiquidTemplate(noteDetailTemplate)
    if (!validation.valid) {
      toast.error(`Template error: ${validation.error}`)
      return
    }

    setSavingDetail(true)
    try {
      await spacesApi.updateNoteDetailTemplate(spaceId, noteDetailTemplate || null)
      await refreshSpaces()
      toast.success("Detail template saved")
    } catch (error) {
      toast.error(`Save failed: ${error instanceof Error ? error.message : "Unknown error"}`)
    } finally {
      setSavingDetail(false)
    }
  }

  const handleSaveListTemplate = async () => {
    if (!spaceId) return

    const validation = validateLiquidTemplate(noteListTemplate)
    if (!validation.valid) {
      toast.error(`Template error: ${validation.error}`)
      return
    }

    setSavingList(true)
    try {
      await spacesApi.updateNoteListTemplate(spaceId, noteListTemplate || null)
      await refreshSpaces()
      toast.success("List template saved")
    } catch (error) {
      toast.error(`Save failed: ${error instanceof Error ? error.message : "Unknown error"}`)
    } finally {
      setSavingList(false)
    }
  }

  const defaultDetailTemplate = `<h1>{{ note.fields.title | default: "Note #" | append: note.id }}</h1>

<div class="metadata">
  <span>By {{ note.author }} on {{ note.created_at | date: "%B %d, %Y at %I:%M %p" }}</span>
  {% if note.edited_at %}
    <span> • Edited {{ note.edited_at | date: "%B %d, %Y" }}</span>
  {% endif %}
</div>

{% for field in space.fields %}
  {% unless field.name == "title" %}
    <div class="field">
      <h3>{{ field.name }}</h3>
      <div>
        {% if field.type == "markdown" %}
          {{ note.fields[field.name] | markdown }}
        {% else %}
          {{ note.fields[field.name] | default: "-" }}
        {% endif %}
      </div>
    </div>
  {% endunless %}
{% endfor %}`

  const defaultListTemplate = `<div class="note-item">
  <h3>{{ note.fields.title | default: "Note #" | append: note.id }}</h3>
  <div class="meta">
    {{ note.created_at | date: "%B %d" }} by {{ note.author }}
    {% if note.comment_count > 0 %}
      • {{ note.comment_count }} comment{% if note.comment_count > 1 %}s{% endif %}
    {% endif %}
  </div>
  {% if note.fields.body %}
    <p>{{ note.fields.body | truncate: 100 }}</p>
  {% endif %}
</div>`

  return (
    <div>
      <NoteBreadcrumb spaceId={spaceId!} spaceName={space.name} currentPage="Templates" showNoteAsLink={false} />

      <h1 className="text-2xl font-bold my-4">Space Templates</h1>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Note Detail Template</CardTitle>
            <CardDescription>
              Customize how individual notes are displayed. Leave empty to use the default layout.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="detail-template">Template (Liquid syntax)</Label>
                <Textarea
                  id="detail-template"
                  value={noteDetailTemplate}
                  onChange={e => setNoteDetailTemplate(e.target.value)}
                  className="font-mono text-sm"
                  rows={15}
                  placeholder={defaultDetailTemplate}
                />
              </div>

              <div className="text-sm text-gray-600">
                <p className="font-semibold mb-1">Available variables:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>
                    <code>note.id</code>, <code>note.author</code>, <code>note.created_at</code>, <code>note.edited_at</code>
                  </li>
                  <li>
                    <code>note.fields.{"{field_name}"}</code> - Access any field value
                  </li>
                  <li>
                    <code>space.name</code>, <code>space.fields</code> - Space information
                  </li>
                </ul>
                <p className="font-semibold mt-2 mb-1">Available filters:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>
                    <code>date</code> - Format dates
                  </li>
                  <li>
                    <code>markdown</code> - Render markdown content
                  </li>
                  <li>
                    <code>default</code> - Provide fallback value
                  </li>
                  <li>
                    <code>truncate</code> - Limit text length
                  </li>
                </ul>
              </div>

              <div className="flex gap-2 mt-4">
                <Button onClick={handleSaveDetailTemplate} disabled={savingDetail}>
                  {savingDetail ? "Saving..." : "Save Detail Template"}
                </Button>
                <Button variant="outline" onClick={() => setNoteDetailTemplate("")}>
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Note List Template</CardTitle>
            <CardDescription>
              Customize how notes appear in list views. Leave empty to use the default table view.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="list-template">Template (Liquid syntax)</Label>
                <Textarea
                  id="list-template"
                  value={noteListTemplate}
                  onChange={e => setNoteListTemplate(e.target.value)}
                  className="font-mono text-sm"
                  rows={10}
                  placeholder={defaultListTemplate}
                />
              </div>

              <div className="flex gap-2 mt-4">
                <Button onClick={handleSaveListTemplate} disabled={savingList}>
                  {savingList ? "Saving..." : "Save List Template"}
                </Button>
                <Button variant="outline" onClick={() => setNoteListTemplate("")}>
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => validateAllTemplates()}>
            Validate All Templates
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/spaces/${spaceId}/fields`}>Fields</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/spaces/${spaceId}/filters`}>Filters</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
