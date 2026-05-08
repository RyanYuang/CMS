import { http } from './http'
import type { OkResponse, PageResult, UserCreate, UserItem, UserUpdate } from './types'

export type UserListParams = {
  keyword?: string
  is_active?: boolean
  role_id?: number
  page?: number
  page_size?: number
}

export const usersApi = {
  list(params: UserListParams) {
    return http.get<PageResult<UserItem>, PageResult<UserItem>>('/v1/users', { params })
  },
  create(payload: UserCreate) {
    return http.post<UserItem, UserItem>('/v1/users', payload)
  },
  update(id: number, payload: UserUpdate) {
    return http.patch<UserItem, UserItem>(`/v1/users/${id}`, payload)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/users/${id}`)
  },
}
