import type { Filter } from "@/lib/api/notes"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface FilterDropdownProps {
  filters: Filter[]
  selectedFilter: Filter | null
  onFilterSelect: (filter: Filter | null) => void
}

export function FilterDropdown({ filters, selectedFilter, onFilterSelect }: FilterDropdownProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">{selectedFilter ? selectedFilter.title : "All Notes"}</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => onFilterSelect(null)}>All Notes</DropdownMenuItem>
        {filters.map(filter => (
          <DropdownMenuItem key={filter.id} onClick={() => onFilterSelect(filter)}>
            {filter.title}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
