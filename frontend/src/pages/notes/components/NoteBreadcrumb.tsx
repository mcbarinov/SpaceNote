import { Link } from "react-router"
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb"

interface NoteBreadcrumbProps {
  spaceId: string
  spaceName: string
  noteId?: number
  currentPage: string
  showNoteAsLink?: boolean
}

export function NoteBreadcrumb({ spaceId, spaceName, noteId, currentPage, showNoteAsLink = true }: NoteBreadcrumbProps) {
  return (
    <Breadcrumb className="my-4">
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link to={`/notes/${spaceId}`}>Notes / {spaceName}</Link>
          </BreadcrumbLink>
        </BreadcrumbItem>
        {noteId && showNoteAsLink && (
          <>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link to={`/notes/${spaceId}/${noteId}`}>Note #{noteId}</Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
          </>
        )}
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>{currentPage}</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  )
}
