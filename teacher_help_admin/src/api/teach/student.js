import request from '@/utils/request'

// 查询学生列表
export function listStudent(query) {
  return request({
    url: '/teach/student/list',
    method: 'get',
    params: query
  })
}

// 查询学生详细
export function getStudent(studentId) {
  return request({
    url: '/teach/student/' + studentId,
    method: 'get'
  })
}

// 新增学生
export function addStudent(data) {
  return request({
    url: '/teach/student',
    method: 'post',
    data: data
  })
}

// 修改学生
export function updateStudent(data) {
  return request({
    url: '/teach/student',
    method: 'put',
    data: data
  })
}

// 删除学生（支持批量删除）
export function delStudent(studentIds) {
  return request({
    url: '/teach/student/' + studentIds,
    method: 'delete'
  })
}

// 查询家长列表（用于学生关联）
export function listParents() {
  return request({
    url: '/teach/parent/list',
    method: 'get'
  })
}

// 导出学生数据
export function exportStudent(query) {
  return request({
    url: '/teach/student/export',
    method: 'post',
    data: query,
    responseType: 'blob'
  })
}

// Course enrollment is not implemented in the backend yet.
export function getStudentCourses() {
  return Promise.resolve({ data: [] })
}

export function withdrawCourse() {
  return Promise.resolve({ code: 200, msg: 'success' })
}
