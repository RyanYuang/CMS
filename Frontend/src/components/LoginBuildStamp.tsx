import { Typography } from 'antd'
import { usePublicBuildInfo } from '../hooks/usePublicBuildInfo'
import { formatBuildStampTime } from '../utils/format'

export function LoginBuildStamp() {
  const backend = usePublicBuildInfo()

  const feVersion = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '—'
  const feRaw = typeof __BUILD_TIME__ !== 'undefined' ? __BUILD_TIME__ : ''
  const feBuilt = feRaw ? formatBuildStampTime(feRaw) : '—'

  const beVersion = backend?.version?.trim() ? backend.version : '—'
  const beRaw = backend?.build_time?.trim() ?? ''
  const beBuilt = beRaw ? formatBuildStampTime(beRaw) : '—'
  const bePort = backend?.port != null ? String(backend.port) : '—'

  return (
    <div className="login-build-stamp" aria-hidden>
      <Typography.Paragraph type="secondary" className="login-build-stamp__line m-0">
        <span className="login-build-stamp__label">前端</span>
        <span className="login-build-stamp__mono">v{feVersion}</span>
        <span className="login-build-stamp__sep">·</span>
        <span className="login-build-stamp__mono" title={feRaw || undefined}>
          build {feBuilt}
        </span>
      </Typography.Paragraph>
      <Typography.Paragraph type="secondary" className="login-build-stamp__line m-0">
        <span className="login-build-stamp__label">后端</span>
        <span className="login-build-stamp__mono">v{beVersion}</span>
        <span className="login-build-stamp__sep">·</span>
        <span className="login-build-stamp__mono" title={`监听端口 ${bePort}`}>
          :{bePort}
        </span>
        <span className="login-build-stamp__sep">·</span>
        <span className="login-build-stamp__mono" title={beRaw || undefined}>
          build {beBuilt}
        </span>
      </Typography.Paragraph>
    </div>
  )
}
