import { useMemo } from 'react'
import { getCurrentUser } from '../utils/auth'

export function useCurrentUser() {
  return useMemo(() => getCurrentUser(), [])
}
