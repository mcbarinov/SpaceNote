import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { commentsApi, type Comment } from "@/lib/api"
import { formatDateTime } from "@/lib/formatters"

interface CommentsProps {
  spaceId: string
  noteId: number
}

export function Comments({ spaceId, noteId }: CommentsProps) {
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState("")
  const [loading, setLoading] = useState(false)

  const loadComments = async () => {
    try {
      const data = await commentsApi.getComments(spaceId, noteId)
      setComments(data)
    } catch (error) {
      console.error("Failed to load comments:", error)
    }
  }

  const addComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim()) return

    try {
      setLoading(true)
      await commentsApi.createComment(spaceId, noteId, { content: newComment.trim() })
      setNewComment("")
      loadComments()
    } catch (error) {
      console.error("Failed to create comment:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const fetchComments = async () => {
      try {
        const data = await commentsApi.getComments(spaceId, noteId)
        setComments(data)
      } catch (error) {
        console.error("Failed to load comments:", error)
      }
    }
    fetchComments()
  }, [spaceId, noteId])

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Comments</h2>

      <form onSubmit={addComment} className="space-y-4">
        <Textarea
          value={newComment}
          onChange={e => setNewComment(e.target.value)}
          placeholder="Write a comment..."
          rows={3}
          disabled={loading}
        />
        <Button type="submit" disabled={loading || !newComment.trim()}>
          {loading ? "Adding..." : "Add Comment"}
        </Button>
      </form>

      <div className="space-y-4">
        {comments.map(comment => (
          <div key={comment.id} className="border-b border-gray-200 pb-4 last:border-b-0">
            <div className="flex items-center space-x-2 mb-2">
              <span className="font-medium text-gray-900">{comment.author}</span>
              <span className="text-gray-500">•</span>
              <span className="text-sm text-gray-500">{formatDateTime(comment.created_at)}</span>
            </div>
            <p className="text-gray-900 whitespace-pre-wrap">{comment.content}</p>
          </div>
        ))}
        {comments.length === 0 && <div className="text-gray-500 text-center py-4">No comments yet.</div>}
      </div>
    </div>
  )
}
