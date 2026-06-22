import { http } from '@/http/http'
import type { TeachPageRes } from './schedule'

export type AttendanceStatus = 0 | 1 | 2 | 3 | 4

export interface AttendanceRecord {
  id: number
  eventId: number
  studentId: number
  studentName: string
  status: AttendanceStatus
  statusName?: string
  isCountable?: number
  checkInTime?: string
  checkInMethod?: string
  notes?: string
}

export interface AttendanceStat {
  eventId: number
  total: number
  planned: number
  present: number
  late: number
  excused: number
  absent: number
  notArrived: number
  attendanceRate: number
}

export function listAttendance(query: Record<string, any>) {
  return http.get<null>('/teach/mobile/attendance/list', query) as Promise<TeachPageRes<AttendanceRecord>>
}

export function manualAttendance(data: {
  eventId: number
  studentId: number
  status: AttendanceStatus
  notes?: string
}) {
  return http.post<void>('/teach/mobile/attendance/manual', data)
}

export function batchManualAttendance(data: {
  eventId: number
  studentIds: number[]
  status: AttendanceStatus
  notes?: string
}) {
  return http.post<void>('/teach/mobile/attendance/batch', data)
}

export function getAttendanceStat(eventId: number | string) {
  return http.get<AttendanceStat>(`/teach/mobile/attendance/stat/${eventId}`)
}
