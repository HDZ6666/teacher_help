import request from '@/utils/request'

// 课次调课（改时间/老师/教室，后端做冲突校验）
export function rescheduleLesson(data) {
  return request({ url: '/teach/schedule/lesson/reschedule', method: 'put', data })
}

// 可加入课次的临时学员（非本班、持有本课程有效账户）
export function listTempStudentOptions(query) {
  return request({ url: '/teach/schedule/lesson/temp-student/options', method: 'get', params: query })
}

// 添加临时学员（课次已点名时需带到课状态与扣课数量）
export function addTempStudent(data) {
  return request({ url: '/teach/schedule/lesson/temp-student', method: 'post', data })
}

// 移出临时学员（仅未点名课次）
export function removeTempStudent(eventId, studentId) {
  return request({ url: `/teach/schedule/lesson/temp-student/${eventId}/${studentId}`, method: 'delete' })
}

// 班级按周重复排课
export function weeklySchedule(data) {
  return request({ url: '/teach/schedule/lesson/weekly', method: 'post', data, timeout: 60000 })
}
