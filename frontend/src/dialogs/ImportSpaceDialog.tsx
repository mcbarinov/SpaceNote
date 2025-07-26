import { useState } from "react"
import { useNavigate } from "react-router"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Upload, AlertCircle } from "lucide-react"
import { spacesApi, type ImportResult, type Space } from "@/lib/api/spaces"
import { useSpacesStore } from "@/stores/spacesStore"
import type { BaseDialogProps } from "@/lib/dialog/types"

type ImportStatus = "idle" | "loading" | "success" | "error"

export default function ImportSpaceDialog({ onClose }: BaseDialogProps) {
  const navigate = useNavigate()
  const { loadSpaces } = useSpacesStore()
  const [status, setStatus] = useState<ImportStatus>("idle")
  const [message, setMessage] = useState<string>("")
  const [fileData, setFileData] = useState<{ space: Space; notes?: unknown[]; comments?: unknown[] } | null>(null)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const data = JSON.parse(text)

      if (data && typeof data === "object" && "space" in data) {
        setFileData(data as { space: Space; notes?: unknown[]; comments?: unknown[] })
        setStatus("idle")
        setMessage("")
      } else {
        setStatus("error")
        setMessage("Invalid file format: missing space data")
        setFileData(null)
      }
    } catch (err) {
      setStatus("error")
      setMessage("Failed to read file: " + (err instanceof Error ? err.message : "Unknown error"))
      setFileData(null)
    }
  }

  const handleImport = async () => {
    if (!fileData) return

    setStatus("loading")

    try {
      const result = await spacesApi.importSpace(fileData)
      setImportResult(result)
      setStatus("success")
      await loadSpaces()
      onClose()
      navigate(`/notes/${result.space_id}`)
    } catch (err) {
      setStatus("error")
      setMessage(err instanceof Error ? err.message : "Import failed")
    }
  }

  const handleClose = () => {
    setFileData(null)
    setImportResult(null)
    setStatus("idle")
    setMessage("")
    onClose()
  }

  return (
    <Dialog open={true} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Import Space</DialogTitle>
          <DialogDescription>Import a space from a JSON file exported from SpaceNote</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Input type="file" accept=".json" onChange={handleFileChange} className="cursor-pointer" />
          </div>

          {status === "error" && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}

          {fileData && (
            <div className="border rounded-lg p-4 space-y-2">
              <h3 className="font-semibold">Space Preview</h3>
              <div className="text-sm space-y-1">
                <p>
                  <strong>ID:</strong> {fileData.space.id}
                </p>
                <p>
                  <strong>Name:</strong> {fileData.space.name}
                </p>
                <p>
                  <strong>Fields:</strong> {fileData.space.fields.length}
                </p>
                <p>
                  <strong>Filters:</strong> {fileData.space.filters.length}
                </p>
                {fileData.notes && (
                  <p>
                    <strong>Notes:</strong> {fileData.notes.length}
                  </p>
                )}
                {fileData.comments && (
                  <p>
                    <strong>Comments:</strong> {fileData.comments.length}
                  </p>
                )}
              </div>
            </div>
          )}

          {status === "success" && importResult && (
            <Alert>
              <Upload className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <p className="font-semibold">Import successful!</p>
                  <p>Space ID: {importResult.space_id}</p>
                  <p>Notes imported: {importResult.notes_imported}</p>
                  <p>Comments imported: {importResult.comments_imported}</p>
                  {importResult.warnings.length > 0 && (
                    <div className="mt-2">
                      <p className="font-semibold">Warnings:</p>
                      <ul className="list-disc list-inside text-sm">
                        {importResult.warnings.map((warning, i) => (
                          <li key={i}>{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          {status !== "success" && (
            <>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleImport} disabled={!fileData || status === "loading"}>
                {status === "loading" ? "Importing..." : "Import"}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
