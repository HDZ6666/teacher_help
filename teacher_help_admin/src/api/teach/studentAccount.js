import request from '@/utils/request'

// 报读情况（学员课程账户）分页列表
export function listCourseAccount(query) {
  return request({ url: '/teach/student-account/list', method: 'get', params: query })
}

// 课程账户操作日志（studentId 或 accountId）
export function listCourseAccountLog(query) {
  return request({ url: '/teach/student-account/logs', method: 'get', params: query })
}

// 批量转课 / 课时清零 / 改有效期 / 停课 / 复课 / 结课（action: transfer|clear|validity|stop|resume|complete）
export function courseAccountAction(action, data) {
  return request({ url: '/teach/student-account/' + action, method: 'post', data, timeout: 60000 })
}

// 缴费收据
export function getOrderReceipt(orderId) {
  return request({ url: '/teach/student-account/receipt/' + orderId, method: 'get' })
}

// 学员详情：上课记录 / 考勤记录 / 成长档案（点评）
export function listStudentLessons(studentId, query) {
  return request({ url: '/teach/student-account/student/' + studentId + '/lessons', method: 'get', params: query })
}

export function listStudentCheckins(studentId, query) {
  return request({ url: '/teach/student-account/student/' + studentId + '/checkins', method: 'get', params: query })
}

export function listStudentComments(studentId, query) {
  return request({ url: '/teach/student-account/student/' + studentId + '/comments', method: 'get', params: query })
}

// 跟进记录
export function listStudentFollow(query) {
  return request({ url: '/teach/student-follow/list', method: 'get', params: query })
}

export function addStudentFollow(data) {
  return request({ url: '/teach/student-follow', method: 'post', data })
}

export function updateStudentFollow(data) {
  return request({ url: '/teach/student-follow', method: 'put', data })
}

export function delStudentFollow(ids) {
  return request({ url: '/teach/student-follow/' + ids, method: 'delete' })
}

// Excel 导入（上传 multipart，返回 { success, total, successCount, errorCount, errors }）
export function uploadImportFile(url, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({ url, method: 'post', data: formData, timeout: 120000, headers: { 'Content-Type': 'multipart/form-data', repeatSubmit: false } })
}
