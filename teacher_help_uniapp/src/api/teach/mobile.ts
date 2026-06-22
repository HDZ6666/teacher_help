import { http } from '@/http/http'

export interface MobileProfile {
  userId: number
  username: string
  nickname?: string
  phone?: string
  teacherId?: number | null
  roles?: string[]
  permissions?: string[]
  isAdmin?: boolean
}

export function getMobileProfile() {
  return http.get<MobileProfile>('/teach/mobile/me', undefined, undefined, { hideErrorToast: true })
}
