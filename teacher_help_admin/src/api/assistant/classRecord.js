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

// 点名记录的新增/修改/撤销/导出接口后端尚未实现（点名提交走 /teach/class/{id}/attendance），此处不再封装悬空接口

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
