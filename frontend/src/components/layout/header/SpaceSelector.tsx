import { useLocation, useNavigate } from "react-router"
import { useSpacesStore } from "@/stores/spacesStore"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { ChevronDown } from "lucide-react"

export default function SpaceSelector() {
  const navigate = useNavigate()
  const location = useLocation()
  const { spaces } = useSpacesStore()

  const currentSpaceId = location.pathname.split("/")[2]
  const currentSpace = spaces.find(space => space.id === currentSpaceId)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          {currentSpace?.name || "Select Space"}
          <ChevronDown className="w-3 h-3 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {spaces.map(space => (
          <DropdownMenuItem key={space.id} onClick={() => navigate(`/notes/${space.id}`)}>
            {space.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
