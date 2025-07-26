import { useParams, Link } from "react-router"
import { useSpacesStore } from "@/stores/spacesStore"
import { FieldsTable } from "./components/FieldsTable"
import { ListFieldsConfig } from "./components/ListFieldsConfig"
import { HiddenFieldsConfig } from "./components/HiddenFieldsConfig"
import { Button } from "@/components/ui/button"

export default function SpaceFields() {
  const { spaceId } = useParams<{ spaceId: string }>()
  const space = useSpacesStore(state => state.getSpace(spaceId || ""))

  if (!space || !spaceId) {
    return <div className="mt-4">Loading...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center my-4">
        <h1 className="text-2xl font-bold">Fields / {space.name}</h1>
        <Button asChild variant="outline">
          <Link to={`/spaces/${spaceId}/templates`}>Templates</Link>
        </Button>
      </div>

      <FieldsTable fields={space.fields} />

      <div className="mt-8 space-y-8">
        <ListFieldsConfig spaceId={spaceId} initialFields={space.list_fields} availableFields={space.fields} />

        <HiddenFieldsConfig spaceId={spaceId} initialFields={space.hidden_create_fields} availableFields={space.fields} />
      </div>
    </div>
  )
}
