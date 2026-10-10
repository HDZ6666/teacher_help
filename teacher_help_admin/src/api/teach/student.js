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
export function listParents(query) {
  return request({
    url: '/teach/parent/list',
    method: 'get',
    params: query
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

// 提交学生报名/续费
export function submitStudentEnroll(data) {
  return request({
    url: '/teach/student/enroll',
    method: 'post',
    data
  })
}

// 查询学生报读课程
export function getStudentCourses(studentId) {
  return request({
    url: '/teach/student/' + studentId + '/courses',
    method: 'get'
  })
}

// 查询学生消费订单
export function getStudentOrders(studentId) {
  return request({
    url: '/teach/student/' + studentId + '/orders',
    method: 'get'
  })
}

// 退课接口（退课退款、库存回滚）后端尚未实现，不提供前端假成功封装

// 跟进人/学管师候选员工（role: follower | advisor）
export function listStaffOptions(role, keyword) {
  return request({
    url: '/teach/student/staff-options',
    method: 'get',
    params: { role, keyword }
  })
}

// 批量分配跟进人/学管师（userId 为空表示改为待分配）
export function assignStudentStaff(data) {
  return request({
    url: '/teach/student/assign',
    method: 'put',
    data: data
  })
}
