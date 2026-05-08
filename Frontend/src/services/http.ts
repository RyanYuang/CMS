import { message } from 'antd'
import axios from 'axios'

export const TOKEN_KEY = 'cms_token'
const AUTH_FLAG_KEY = 'isAuthenticated'
const USER_KEY = 'cms_user'

type ApiErrorDetail = {
  message?: string
}

type ApiErrorData = {
  detail?: string | ApiErrorDetail
  message?: string
}

export function extractApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiErrorData>(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }
    if (detail && typeof detail === 'object' && typeof detail.message === 'string') {
      return detail.message
    }
    if (typeof error.response?.data?.message === 'string') {
      return error.response.data.message
    }
    if (typeof error.message === 'string') {
      return error.message
    }
  }
  if (error instanceof Error) {
    return error.message
  }
  return '请求失败，请稍后重试'
}

export function clearAuthStorage() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(AUTH_FLAG_KEY)
  localStorage.removeItem(USER_KEY)
}

export const http = axios.create({
  baseURL: '/api',
  timeout: 12000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // #region agent log
    fetch('http://127.0.0.1:7473/ingest/7897f39d-d50b-4fd8-bb95-8efbd575b269', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '308264' },
      body: JSON.stringify({
        sessionId: '308264',
        runId: 'frontend-pre-fix',
        hypothesisId: 'F3',
        location: 'src/services/http.ts:response.error',
        message: 'http interceptor caught error',
        data: {
          status: axios.isAxiosError(error) ? (error.response?.status ?? null) : null,
          code: axios.isAxiosError(error) ? (error.code ?? null) : null,
          requestPath: axios.isAxiosError(error) ? (error.config?.url ?? null) : null,
          pathname: window.location.pathname,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
    // #endregion
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      clearAuthStorage()
      // #region agent log
      fetch('http://127.0.0.1:7473/ingest/7897f39d-d50b-4fd8-bb95-8efbd575b269', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '308264' },
        body: JSON.stringify({
          sessionId: '308264',
          runId: 'frontend-pre-fix',
          hypothesisId: 'F4',
          location: 'src/services/http.ts:response.error',
          message: 'unauthorized redirect decision',
          data: {
            pathname: window.location.pathname,
            redirectTo: '/login',
          },
          timestamp: Date.now(),
        }),
      }).catch(() => {})
      // #endregion
      const loginPath = `${import.meta.env.BASE_URL.replace(/\/$/, '')}/login`
      if (window.location.pathname !== loginPath) {
        window.location.href = loginPath
      }
    }
    const msg = extractApiErrorMessage(error)
    message.error(msg)
    return Promise.reject(new Error(msg))
  },
)
