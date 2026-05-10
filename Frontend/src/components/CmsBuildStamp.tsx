/**
 * 侧栏构建信息：前端来自 Vite 注入；后端版本 / 端口 / 构建时间来自 /api/v1/public/build。
 */

import { usePublicBuildInfo } from '../hooks/usePublicBuildInfo'
import { formatBuildStampTime } from '../utils/format'

export function CmsBuildStamp() {
  const backend = usePublicBuildInfo()

  const feVersion = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '—'
  const feRaw = typeof __BUILD_TIME__ !== 'undefined' ? __BUILD_TIME__ : ''
  const feBuilt = feRaw ? formatBuildStampTime(feRaw) : '—'

  const beVersion = backend?.version?.trim() ? backend.version : '—'
  const beRaw = backend?.build_time?.trim() ?? ''
  const beBuilt = beRaw ? formatBuildStampTime(beRaw) : '—'
  const bePort = backend?.port != null ? String(backend.port) : '—'

  return (
    <div className="sider-build-stamp" aria-hidden>
      <div className="sider-build-stamp__row">
        <span className="sider-build-stamp__label">前端</span>
        <span className="sider-build-stamp__mono">v{feVersion}</span>
        <span className="sider-build-stamp__sep">·</span>
        <span className="sider-build-stamp__mono" title={feRaw || undefined}>
          build {feBuilt}
        </span>
      </div>
      <div className="sider-build-stamp__row">
        <span className="sider-build-stamp__label">后端</span>
        <span className="sider-build-stamp__mono">v{beVersion}</span>
        <span className="sider-build-stamp__sep">·</span>
        <span className="sider-build-stamp__mono" title={`监听端口 ${bePort}`}>
          :{bePort}
        </span>
        <span className="sider-build-stamp__sep">·</span>
        <span className="sider-build-stamp__mono" title={beRaw || undefined}>
          build {beBuilt}
        </span>
      </div>
    </div>
  )
}
