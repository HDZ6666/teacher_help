import { http } from '@/http/http'

export interface TeachPageRes<T> extends IResData<null> {
  rows: T[]
  total: number
  pageNum?: number
  pageSize?: number
}

export interface ScheduleStudent {
  id?: number
  studentId: number
  studentName: string
  status: number
  checkInTime?: string
  notes?: string
  remainingCount?: number | null
  lowRemaining?: boolean
}

export interface ScheduleEvent {
  id: number
  teacherId?: number
  teacherName?: string
  courseId?: number
  courseName?: string
  subjectCode?: string
  subjectName?: string
  startTime: string
  endTime: string
  eventDate?: string
  status?: string
  statusName?: string
  cachedPlanned?: number
  cachedPresent?: number
  cachedLate?: number
  cachedExcused?: number
  cachedAbsent?: number
  cachedRate?: number
  remark?: string
  students?: ScheduleStudent[]
}

export interface ScheduleQuery {
  pageNum?: number
  pageSize?: number
  teacherId?: number
  courseId?: number
  subjectCode?: string
  status?: string
  eventDate?: string
  startTime?: string
  endTime?: string
}

export function listScheduleEvent(query: ScheduleQuery = {}) {
  return http.get<null>('/teach/mobile/schedule/list', query) as Promise<TeachPageRes<ScheduleEvent>>
}

export function getScheduleEvent(eventId: number | string) {
  return http.get<ScheduleEvent>(`/teach/mobile/schedule/${eventId}`)
}

export function finishScheduleEvent(eventId: number | string) {
  return http.post<void>(`/teach/mobile/schedule/${eventId}/finish`)
}
