import { useEffect, useState } from 'react'

export type PublicBuildInfo = {
  version: string
  build_time: string
  port: number
}

function parseBuildPayload(data: unknown): PublicBuildInfo | null {
  if (!data || typeof data !== 'object') return null
  const o = data as Record<string, unknown>
  if (typeof o.version !== 'string') return null
  if (typeof o.build_time !== 'string') return null
  const port = o.port
  if (typeof port !== 'number' || !Number.isFinite(port)) return null
  return { version: o.version, build_time: o.build_time, port }
}

/** 匿名 GET /api/v1/public/build（与 axios 拦截器分离，避免不可达时全局报错） */
export function usePublicBuildInfo(): PublicBuildInfo | null {
  const [info, setInfo] = useState<PublicBuildInfo | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch('/api/v1/public/build')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((data: unknown) => {
        if (!cancelled) setInfo(parseBuildPayload(data))
      })
      .catch(() => {
        if (!cancelled) setInfo(null)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return info
}
