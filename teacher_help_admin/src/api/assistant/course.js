import request from '@/utils/request'

// 查询课程列表
export function listCourse(query) {
  return request({
    url: '/teach/course/list',
    method: 'get',
    params: query
  })
}

// 查询课程详情
export function getCourse(courseId) {
  return request({
    url: '/teach/course/' + courseId,
    method: 'get'
  })
}

// 新增课程
export function addCourse(data) {
  return request({
    url: '/teach/course',
    method: 'post',
    data
  })
}

// 批量新增课程
export function batchAddCourse(data) {
  return request({
    url: '/teach/course/batch',
    method: 'post',
    data
  })
}

// 修改课程
export function updateCourse(data) {
  return request({
    url: '/teach/course',
    method: 'put',
    data
  })
}

// 修改课程状态
export function changeCourseStatus(data) {
  return request({
    url: '/teach/course/changeStatus',
    method: 'put',
    data
  })
}

// 删除课程
export function delCourse(courseIds) {
  return request({
    url: '/teach/course/' + courseIds,
    method: 'delete'
  })
}

// 课程选择项
export function listCourseOptions(query) {
  return request({
    url: '/teach/course/options',
    method: 'get',
    params: query
  })
}

// 查询套餐列表
export function listCoursePackage(query) {
  return request({
    url: '/teach/course/package/list',
    method: 'get',
    params: query
  })
}

// 查询套餐详情
export function getCoursePackage(packageId) {
  return request({
    url: '/teach/course/package/' + packageId,
    method: 'get'
  })
}

// 新增套餐
export function addCoursePackage(data) {
  return request({
    url: '/teach/course/package',
    method: 'post',
    data
  })
}

// 修改套餐
export function updateCoursePackage(data) {
  return request({
    url: '/teach/course/package',
    method: 'put',
    data
  })
}

// 修改套餐状态
export function changeCoursePackageStatus(data) {
  return request({
    url: '/teach/course/package/changeStatus',
    method: 'put',
    data
  })
}

// 删除套餐
export function delCoursePackage(packageIds) {
  return request({
    url: '/teach/course/package/' + packageIds,
    method: 'delete'
  })
}
