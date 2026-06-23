import request from '@/utils/request'

// 查询班级列表
export function listClass(query) {
  return request({
    url: '/teach/class/list',
    method: 'get',
    params: query
  })
}

// 查询班级选择项
export function listClassOptions(query) {
  return request({
    url: '/teach/class/options',
    method: 'get',
    params: query
  })
}

// 查询班级详情
export function getClass(classId) {
  return request({
    url: '/teach/class/' + classId,
    method: 'get'
  })
}

// 新增班级
export function addClass(data) {
  return request({
    url: '/teach/class',
    method: 'post',
    data
  })
}

// 修改班级
export function updateClass(data) {
  return request({
    url: '/teach/class',
    method: 'put',
    data
  })
}

// 删除班级
export function delClass(classIds) {
  return request({
    url: '/teach/class/' + classIds,
    method: 'delete'
  })
}

// 修改充值购时开关
export function changeClassRecharge(data) {
  return request({
    url: '/teach/class/changeRecharge',
    method: 'put',
    data
  })
}

// 查询班级学员
export function listClassStudents(classId) {
  return request({
    url: '/teach/class/' + classId + '/students',
    method: 'get'
  })
}

// 查询可添加学员
export function listAvailableClassStudents(classId, query) {
  return request({
    url: '/teach/class/' + classId + '/available-students',
    method: 'get',
    params: query
  })
}

// 添加班级学员
export function addClassStudents(classId, data) {
  return request({
    url: '/teach/class/' + classId + '/students',
    method: 'post',
    data
  })
}

// 移出班级学员
export function removeClassStudents(classId, studentIds) {
  return request({
    url: '/teach/class/' + classId + '/students/' + studentIds,
    method: 'delete'
  })
}

// 查询班级点名准备数据
export function getClassAttendancePrepare(classId, query) {
  return request({
    url: '/teach/class/' + classId + '/attendance/prepare',
    method: 'get',
    params: query
  })
}

// 查询班级点名记录
export function listClassAttendance(classId) {
  return request({
    url: '/teach/class/' + classId + '/attendance/list',
    method: 'get'
  })
}

// 查询班级点名详情
export function getClassAttendance(attendanceId) {
  return request({
    url: '/teach/class/attendance/' + attendanceId,
    method: 'get'
  })
}

// 提交班级点名
export function submitClassAttendance(classId, data) {
  return request({
    url: '/teach/class/' + classId + '/attendance',
    method: 'post',
    data
  })
}
