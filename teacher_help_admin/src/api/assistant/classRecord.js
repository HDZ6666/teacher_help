import request from '@/utils/request'

// 查询点名记录列表
export function listAttendanceRecord(query) {
  return request({
    url: '/teach/class-record/attendance/list',
    method: 'get',
    params: query
  })
}

// 查询点名记录详细
export function getAttendanceRecord(recordId) {
  return request({
    url: '/teach/class-record/attendance/' + recordId,
    method: 'get'
  })
}

// 撤销点名（整次点名记录，退回已扣课时，课次可重新点名）
export function revokeAttendanceRecord(data) {
  return request({
    url: '/teach/class-record/attendance/revoke',
    method: 'put',
    data: data
  })
}

// 缺课明细标记已补（只记录补课标记，不影响扣课）
export function markMakeupRecord(data) {
  return request({
    url: '/teach/class-record/makeup/mark',
    method: 'put',
    data: data
  })
}

// 导出走 proxy.download('teach/class-record/{attendance|overtime|makeup|absence}/export')；点名提交走 /teach/class/{id}/attendance

// 查询超纲未点列表
export function listOvertimeRecord(query) {
  return request({
    url: '/teach/class-record/overtime/list',
    method: 'get',
    params: query
  })
}

// 查询缺课补课列表
export function listMakeupRecord(query) {
  return request({
    url: '/teach/class-record/makeup/list',
    method: 'get',
    params: query
  })
}

// 查询缺课提醒列表
export function listAbsenceReminder(query) {
  return request({
    url: '/teach/class-record/absence/list',
    method: 'get',
    params: query
  })
}

// 查询请假申请列表
export function listLeaveApplication(query) {
  return request({
    url: '/teach/leave/list',
    method: 'get',
    params: query
  })
}

// 查询请假申请详细
export function getLeaveApplication(leaveId) {
  return request({
    url: '/teach/leave/' + leaveId,
    method: 'get'
  })
}

// 新增请假申请（代请假）
export function addLeaveApplication(data) {
  return request({
    url: '/teach/leave',
    method: 'post',
    data: data
  })
}

// 审批请假申请
export function approveLeaveApplication(data) {
  return request({
    url: '/teach/leave/approve',
    method: 'put',
    data: data
  })
}

// 撤销请假申请
export function delLeaveApplication(leaveIds) {
  return request({
    url: '/teach/leave/' + leaveIds,
    method: 'delete'
  })
}

// 修改单个学员点名（同一课次内改状态/扣课，后端自动退/补扣课时）
export function editAttendanceDetail(data) {
  return request({ url: '/teach/class-record/attendance/detail', method: 'put', data })
}

// 编辑课次（已点名记录的日期/时间/老师/教室/课时/内容）
export function editAttendanceRecord(data) {
  return request({ url: '/teach/class-record/attendance', method: 'put', data })
}

// 开补课班：从缺课记录生成补课课次
export function createMakeupClass(data) {
  return request({ url: '/teach/class-record/makeup/class', method: 'post', data })
}
