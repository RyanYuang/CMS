import { http } from './http'
import type { OkResponse, Tag, TagCreate } from './types'

export const tagsApi = {
  list() {
    return http.get<Tag[], Tag[]>('/v1/tags')
  },
  create(payload: TagCreate) {
    return http.post<Tag, Tag>('/v1/tags', payload)
  },
  update(id: number, payload: TagCreate) {
    return http.patch<Tag, Tag>(`/v1/tags/${id}`, payload)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/tags/${id}`)
  },
}
