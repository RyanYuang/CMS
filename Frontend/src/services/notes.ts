import { http } from './http'
import type {
  Note,
  NoteCount,
  NoteCreate,
  NoteListQuery,
  NoteUpdate,
  OkResponse,
  PageResult,
} from './types'

export const notesApi = {
  list(params: NoteListQuery = {}) {
    return http.get<PageResult<Note>, PageResult<Note>>('/v1/notes', { params })
  },
  count() {
    return http.get<NoteCount, NoteCount>('/v1/notes/count')
  },
  get(id: number) {
    return http.get<Note, Note>(`/v1/notes/${id}`)
  },
  create(payload: NoteCreate) {
    return http.post<Note, Note>('/v1/notes', payload)
  },
  update(id: number, payload: NoteUpdate) {
    return http.patch<Note, Note>(`/v1/notes/${id}`, payload)
  },
  togglePin(id: number) {
    return http.post<Note, Note>(`/v1/notes/${id}/pin`)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/notes/${id}`)
  },
}
