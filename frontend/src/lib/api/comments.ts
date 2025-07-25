import { api } from "./index"

export interface Comment {
  id: number
  note_id: number
  author: string
  content: string
  created_at: string
  edited_at?: string
  parent_id?: number
}

export interface CreateCommentRequest {
  content: string
}

export const commentsApi = {
  getComments: (spaceId: string, noteId: number): Promise<Comment[]> =>
    api.get(`comments?space_id=${spaceId}&note_id=${noteId}`).json(),

  createComment: (spaceId: string, noteId: number, request: CreateCommentRequest): Promise<Comment> =>
    api.post(`comments?space_id=${spaceId}&note_id=${noteId}`, { json: request }).json(),
}
