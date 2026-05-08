import { http } from './http'
import type { OkResponse, SettingItem } from './types'

export const settingsApi = {
  list() {
    return http.get<SettingItem[], SettingItem[]>('/v1/settings')
  },
  upsert(items: SettingItem[]) {
    return http.put<OkResponse, OkResponse>('/v1/settings', items)
  },
}
