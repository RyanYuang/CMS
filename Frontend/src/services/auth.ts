import { clearAuthStorage, http } from './http'
import type { LoginResponse, MeResponse, OkResponse } from './types'

export const authApi = {
  login(username: string, password: string) {
    return http.post<LoginResponse, LoginResponse>('/v1/auth/login', { username, password })
  },
  me() {
    return http.get<MeResponse, MeResponse>('/v1/auth/me')
  },
  async logout() {
    try {
      await http.post<OkResponse, OkResponse>('/v1/auth/logout')
    } finally {
      clearAuthStorage()
    }
  },
}
