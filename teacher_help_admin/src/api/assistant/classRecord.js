import request from '@/utils/request'

// 查询点名记录列表
export function listAttendanceRecord(query) {
  return request({
    url: '/assistant/classRecord/attendance/list',
    method: 'get',
    params: query
  })
}

// 查询点名记录详细
export function getAttendanceRecord(recordId) {
  return request({
    url: '/assistant/classRecord/attendance/' + recordId,
    method: 'get'
  })
}

// 新增点名记录
export function addAttendanceRecord(data) {
  return request({
    url: '/assistant/classRecord/attendance',
    method: 'post',
    data: data
  })
}

// 修改点名记录
export function updateAttendanceRecord(data) {
  return request({
    url: '/assistant/classRecord/attendance',
    method: 'put',
    data: data
  })
}

// 删除点名记录
export function delAttendanceRecord(recordIds) {
  return request({
    url: '/assistant/classRecord/attendance/' + recordIds,
    method: 'delete'
  })
}

// 导出点名记录
export function exportAttendanceRecord(query) {
  return request({
    url: '/assistant/classRecord/attendance/export',
    method: 'post',
    data: query,
    responseType: 'blob'
  })
}

// 查询超纲未点列表
export function listOvertimeRecord(query) {
  return request({
    url: '/assistant/classRecord/overtime/list',
    method: 'get',
    params: query
  })
}

// 查询缺课提醒列表
export function listAbsenceReminder(query) {
  return request({
    url: '/assistant/classRecord/absence/list',
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

