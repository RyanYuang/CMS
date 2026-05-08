import { http } from './http'
import type { AuditAction, AuditLog, PageResult } from './types'

export type AuditListParams = {
  target_type?: string
  target_id?: string
  actor_id?: number
  action?: AuditAction
  page?: number
  page_size?: number
}

export const auditApi = {
  list(params: AuditListParams) {
    return http.get<PageResult<AuditLog>, PageResult<AuditLog>>('/v1/audit', { params })
  },
}
