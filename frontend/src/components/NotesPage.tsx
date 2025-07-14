import { Layout } from "./Layout"
import { useSpaces } from "@/hooks/useSpaces"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { LEGACY_BASE_URL } from "@/lib/api"

export function NotesPage() {
  const { data: spaces, isLoading, error } = useSpaces()

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Notes</h1>
          <p className="text-slate-600">Access your spaces and manage your notes</p>
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
                <div className="text-slate-400 mb-4">📝</div>
                <p className="text-slate-600 font-medium">No spaces available</p>
                <p className="text-slate-500 text-sm mt-1">Contact your administrator to get access to spaces</p>
              </div>
            </CardContent>
          </Card>
        )}

        {spaces && spaces.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {spaces.map((space) => (
              <Card key={space.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">{space.name}</CardTitle>
                  <CardDescription>
                    {space.members.length} {space.members.length === 1 ? 'member' : 'members'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button asChild className="w-full">
                    <a href={`${LEGACY_BASE_URL}/notes/${space.id}`}>
                      Open Space
                    </a>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}