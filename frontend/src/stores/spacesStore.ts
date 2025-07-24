import { create } from "zustand"
import { persist } from "zustand/middleware"
import { spacesApi, type Space } from "@/lib/api/spaces"

interface SpacesState {
  spaces: Space[]
  isLoading: boolean
  error: string | null

  loadSpaces: () => Promise<void>
  refreshSpaces: () => Promise<void>
  getSpace: (spaceId: string) => Space | undefined
}

export const useSpacesStore = create<SpacesState>()(
  persist(
    (set, get) => {
      const fetchSpaces = async (force = false) => {
        const state = get()
        if (!force && (state.isLoading || state.spaces.length > 0)) return

        set({ isLoading: true, error: null })
        try {
          const spaces = await spacesApi.listSpaces()
          set({ spaces, isLoading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "Failed to load spaces",
            isLoading: false,
          })
        }
      }

      return {
        spaces: [],
        isLoading: false,
        error: null,

        loadSpaces: () => fetchSpaces(false),
        refreshSpaces: () => fetchSpaces(true),
        getSpace: (spaceId: string) => get().spaces.find(space => space.id === spaceId),
      }
    },
    {
      name: "spacenote-spaces",
      partialize: state => ({ spaces: state.spaces }),
    }
  )
)
