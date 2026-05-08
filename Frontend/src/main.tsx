import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles/global.css'

// #region agent log
window.addEventListener('error', (event) => {
  fetch('http://127.0.0.1:7473/ingest/7897f39d-d50b-4fd8-bb95-8efbd575b269', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '308264' },
    body: JSON.stringify({
      sessionId: '308264',
      runId: 'frontend-pre-fix',
      hypothesisId: 'F1',
      location: 'src/main.tsx:window.error',
      message: 'global runtime error captured',
      data: {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      },
      timestamp: Date.now(),
    }),
  }).catch(() => {})
})
window.addEventListener('unhandledrejection', (event) => {
  fetch('http://127.0.0.1:7473/ingest/7897f39d-d50b-4fd8-bb95-8efbd575b269', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '308264' },
    body: JSON.stringify({
      sessionId: '308264',
      runId: 'frontend-pre-fix',
      hypothesisId: 'F2',
      location: 'src/main.tsx:unhandledrejection',
      message: 'unhandled promise rejection captured',
      data: {
        reason: String(event.reason ?? 'unknown'),
        pathname: window.location.pathname,
      },
      timestamp: Date.now(),
    }),
  }).catch(() => {})
})
// #endregion

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename="/cms/leowong">
      <App />
    </BrowserRouter>
  </StrictMode>,
)
