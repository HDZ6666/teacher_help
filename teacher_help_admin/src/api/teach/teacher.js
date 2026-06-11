import request from '@/utils/request'

// 查询教师列表
export function listTeacher(query) {
  return request({
    url: '/teach/teacher/list',
    method: 'get',
    params: query
  })
}

// 查询教师详细
export function getTeacher(teacherId) {
  return request({
    url: '/teach/teacher/' + teacherId,
    method: 'get'
  })
}

// 新增教师
export function addTeacher(data) {
  return request({
    url: '/teach/teacher',
    method: 'post',
    data: data
  })
}

// 修改教师
export function updateTeacher(data) {
  return request({
    url: '/teach/teacher',
    method: 'put',
    data: data
  })
}

// 删除教师（支持批量删除）
export function delTeacher(teacherIds) {
  return request({
    url: '/teach/teacher/' + teacherIds,
    method: 'delete'
  })
}



// 导出教师数据
export function exportTeacher(query) {
  return request({
    url: '/teach/teacher/export',
    method: 'post',
    data: query,
    responseType: 'blob'
  })
}

// 获取教师课程列表
export function getTeacherCourses(teacherId) {
  return request({
    url: '/teach/teacher/' + teacherId + '/courses',
    method: 'get'
  })
}

// 获取教师学生列表
export function getTeacherStudents(teacherId) {
  return request({
    url: '/teach/teacher/' + teacherId + '/students',
    method: 'get'
  })
}

// 获取教师统计信息
export function getTeacherStats(teacherId) {
  return request({
    url: '/teach/teacher/' + teacherId + '/stats',
    method: 'get'
  })
}


