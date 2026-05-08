import { http } from './http'
import type { OkResponse, Permission, Role, RoleCreate, RoleUpdate } from './types'

export const rolesApi = {
  list() {
    return http.get<Role[], Role[]>('/v1/roles')
  },
  listPermissions() {
    return http.get<Permission[], Permission[]>('/v1/roles/permissions')
  },
  create(payload: RoleCreate) {
    return http.post<Role, Role>('/v1/roles', payload)
  },
  update(id: number, payload: RoleUpdate) {
    return http.patch<Role, Role>(`/v1/roles/${id}`, payload)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/roles/${id}`)
  },
}
