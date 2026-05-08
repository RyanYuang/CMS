import { http } from './http'
import type { Category, CategoryCreate, CategoryUpdate, OkResponse } from './types'

export const categoriesApi = {
  list() {
    return http.get<Category[], Category[]>('/v1/categories')
  },
  create(payload: CategoryCreate) {
    return http.post<Category, Category>('/v1/categories', payload)
  },
  update(id: number, payload: CategoryUpdate) {
    return http.patch<Category, Category>(`/v1/categories/${id}`, payload)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/categories/${id}`)
  },
}
