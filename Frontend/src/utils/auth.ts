import type { MeResponse } from '../services'
import { clearAuthStorage, TOKEN_KEY } from '../services/http'

const USER_KEY = 'cms_user'

export function getCurrentUser(): MeResponse | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) {
    return null
  }
  try {
    return JSON.parse(raw) as MeResponse
  } catch {
    return null
  }
}

export function setCurrentUser(user: MeResponse) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearCurrentUser() {
  localStorage.removeItem(USER_KEY)
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem(TOKEN_KEY))
}

export function hasPermission(code: string) {
  const user = getCurrentUser()
  return Boolean(user?.permissions?.includes(code))
}

export function logoutLocal() {
  clearCurrentUser()
  clearAuthStorage()
}
