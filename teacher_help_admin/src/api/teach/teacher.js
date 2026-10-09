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

// 批量获取老师课时统计（上月/本月/累计课次与课时、授课班级数）
export function getTeacherStats(teacherIds) {
  return request({
    url: '/teach/teacher/stats',
    method: 'get',
    params: { teacher_ids: (teacherIds || []).join(',') }
  })
}

// 老师详情概览：课时统计 + 授课班级
export function getTeacherOverview(teacherId) {
  return request({
    url: '/teach/teacher/' + teacherId + '/overview',
    method: 'get'
  })
}

// 老师上课记录（按点名记录分页）
export function listTeacherRecords(teacherId, query) {
  return request({
    url: '/teach/teacher/' + teacherId + '/records',
    method: 'get',
    params: query
  })
}
