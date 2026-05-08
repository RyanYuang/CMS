import { http } from './http'
import type { LinkCreate, LinkItem, LinkUpdate, OkResponse } from './types'

export const linksApi = {
  list() {
    return http.get<LinkItem[], LinkItem[]>('/v1/links')
  },
  create(payload: LinkCreate) {
    return http.post<LinkItem, LinkItem>('/v1/links', payload)
  },
  update(id: number, payload: LinkUpdate) {
    return http.patch<LinkItem, LinkItem>(`/v1/links/${id}`, payload)
  },
  reorder(orderedIds: number[]) {
    return http.post<LinkItem[], LinkItem[]>('/v1/links/reorder', { ordered_ids: orderedIds })
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/links/${id}`)
  },
}
