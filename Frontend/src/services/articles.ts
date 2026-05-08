import { http } from './http'
import type {
  ArticleCreate,
  ArticleDetail,
  ArticleListItem,
  ArticleStatus,
  ArticleStatusUpdate,
  ArticleUpdate,
  ArticleVersionOut,
  OkResponse,
  PageResult,
} from './types'

export type ArticleListParams = {
  keyword?: string
  status?: ArticleStatus
  category_id?: number
  tag_id?: number
  author_id?: number
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

export const articlesApi = {
  list(params: ArticleListParams) {
    return http.get<PageResult<ArticleListItem>, PageResult<ArticleListItem>>('/v1/articles', { params })
  },
  get(id: number) {
    return http.get<ArticleDetail, ArticleDetail>(`/v1/articles/${id}`)
  },
  create(payload: ArticleCreate) {
    return http.post<ArticleDetail, ArticleDetail>('/v1/articles', payload)
  },
  update(id: number, payload: ArticleUpdate) {
    return http.patch<ArticleDetail, ArticleDetail>(`/v1/articles/${id}`, payload)
  },
  autosaveDraft(id: number, payload: ArticleUpdate) {
    return http.put<ArticleDetail, ArticleDetail>(`/v1/articles/${id}/draft`, payload)
  },
  changeStatus(id: number, status: ArticleStatus, note?: string) {
    const payload: ArticleStatusUpdate = { status, note }
    return http.post<ArticleDetail, ArticleDetail>(`/v1/articles/${id}/status`, payload)
  },
  listVersions(id: number) {
    return http.get<ArticleVersionOut[], ArticleVersionOut[]>(`/v1/articles/${id}/versions`)
  },
  rollback(id: number, version: number) {
    return http.post<ArticleDetail, ArticleDetail>(`/v1/articles/${id}/rollback/${version}`)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/articles/${id}`)
  },
}
