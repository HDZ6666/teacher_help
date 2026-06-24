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

// 新增点名记录
export function addAttendanceRecord(data) {
  return request({
    url: '/teach/class-record/attendance',
    method: 'post',
    data: data
  })
}

// 修改点名记录
export function updateAttendanceRecord(data) {
  return request({
    url: '/teach/class-record/attendance',
    method: 'put',
    data: data
  })
}

// 删除点名记录
export function delAttendanceRecord(recordIds) {
  return request({
    url: '/teach/class-record/attendance/' + recordIds,
    method: 'delete'
  })
}

// 导出点名记录
export function exportAttendanceRecord(query) {
  return request({
    url: '/teach/class-record/attendance/export',
    method: 'post',
    data: query,
    responseType: 'blob'
  })
}

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
    url: '/assistant/classRecord/leave/list',
    method: 'get',
    params: query
  })
}

// 查询请假由来列表
export function listLeaveReason(query) {
  return request({
    url: '/assistant/classRecord/leaveReason/list',
    method: 'get',
    params: query
  })
}
