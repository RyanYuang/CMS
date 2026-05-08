import { http } from './http'
import type {
  MusicTrack,
  MusicTrackCount,
  MusicTrackCreate,
  MusicTrackListQuery,
  MusicTrackUpdate,
  OkResponse,
  PageResult,
} from './types'

export const musicApi = {
  list(params: MusicTrackListQuery = {}) {
    return http.get<PageResult<MusicTrack>, PageResult<MusicTrack>>('/v1/music', { params })
  },
  count() {
    return http.get<MusicTrackCount, MusicTrackCount>('/v1/music/count')
  },
  get(id: number) {
    return http.get<MusicTrack, MusicTrack>(`/v1/music/${id}`)
  },
  create(payload: MusicTrackCreate) {
    return http.post<MusicTrack, MusicTrack>('/v1/music', payload)
  },
  update(id: number, payload: MusicTrackUpdate) {
    return http.patch<MusicTrack, MusicTrack>(`/v1/music/${id}`, payload)
  },
  togglePin(id: number) {
    return http.post<MusicTrack, MusicTrack>(`/v1/music/${id}/pin`)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/music/${id}`)
  },
}
