import { useQuery } from "@tanstack/react-query"
import { spacesApi } from "@/lib/api"

export function useSpaces() {
  return useQuery({
    queryKey: ["spaces"],
    queryFn: () => spacesApi.list(),
  })
}