import { http } from './http'
import type { AssetItem, AssetKind, OkResponse, PageResult } from './types'

export type AssetListParams = {
  kind?: AssetKind
  is_orphan?: boolean
  keyword?: string
  page?: number
  page_size?: number
}

export const assetsApi = {
  list(params: AssetListParams) {
    return http.get<PageResult<AssetItem>, PageResult<AssetItem>>('/v1/assets', { params })
  },
  upload(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return http.post<AssetItem, AssetItem>('/v1/assets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/assets/${id}`)
  },
  cleanupOrphans(dryRun = true) {
    return http.post<{ removed: number; scanned: number }, { removed: number; scanned: number }>(
      '/v1/assets/cleanup-orphans',
      null,
      { params: { dry_run: dryRun } },
    )
  },
}
