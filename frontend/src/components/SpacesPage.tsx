import { Layout } from "./layout/Layout"
import { useSpaces } from "@/hooks/useSpaces"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { LEGACY_BASE_URL } from "@/lib/api"

export function SpacesPage() {
  const { data: spaces, isLoading, error } = useSpaces()

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Spaces</h1>
            <p className="text-slate-600">Manage your spaces and configure settings</p>
          </div>
          <Button asChild>
            <a href={`${LEGACY_BASE_URL}/spaces/create`}>Create Space</a>
          </Button>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-slate-500">Loading spaces...</p>
            </div>
          </div>
        )}

        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-red-600 mb-2">⚠️</div>
                <p className="text-red-800 font-medium">Failed to load spaces</p>
                <p className="text-red-600 text-sm mt-1">Please try again later</p>
              </div>
            </CardContent>
          </Card>
        )}

        {spaces && spaces.length === 0 && (
          <Card className="border-slate-200">
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <div className="text-slate-400 mb-4">🏗️</div>
                <p className="text-slate-600 font-medium">No spaces available</p>
                <p className="text-slate-500 text-sm mt-1">Create your first space to get started</p>
              </div>
            </CardContent>
          </Card>
        )}

        {spaces && spaces.length > 0 && (
          <div className="space-y-4">
            {spaces.map((space) => (
              <Card key={space.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">{space.name}</CardTitle>
                      <CardDescription className="text-sm text-slate-500">
                        ID: {space.id}
                      </CardDescription>
                    </div>
                    <Button asChild size="sm">
                      <a href={`${LEGACY_BASE_URL}/notes/${space.id}`}>Open</a>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="flex flex-col">
                      <span className="text-slate-500">Members</span>
                      <a 
                        href={`${LEGACY_BASE_URL}/spaces/${space.id}/members`}
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {space.members.length}
                      </a>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-slate-500">Fields</span>
                      <a 
                        href={`${LEGACY_BASE_URL}/spaces/${space.id}/fields`}
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {space.fields.length}
                      </a>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-slate-500">Filters</span>
                      <a 
                        href={`${LEGACY_BASE_URL}/spaces/${space.id}/filters`}
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {space.filters.length}
                      </a>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-slate-500">Telegram</span>
                      <a 
                        href={`${LEGACY_BASE_URL}/spaces/${space.id}/telegram`}
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {space.telegram?.enabled ? "✓" : "✗"}
                      </a>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}