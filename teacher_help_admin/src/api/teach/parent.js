import request from '@/utils/request'

// 查询家长列表
export function listParent(query) {
  return request({
    url: '/teach/parent/list',
    method: 'get',
    params: query
  })
}

// 查询家长详细
export function getParent(parentId) {
  return request({
    url: '/teach/parent/' + parentId,
    method: 'get'
  })
}

// 新增家长
export function addParent(data) {
  return request({
    url: '/teach/parent',
    method: 'post',
    data: data
  })
}

// 修改家长
export function updateParent(data) {
  return request({
    url: '/teach/parent',
    method: 'put',
    data: data
  })
}

// 删除家长（支持批量删除）
export function delParent(parentIds) {
  return request({
    url: '/teach/parent/' + parentIds,
    method: 'delete'
  })
}

// 导出家长数据
export function exportParent(query) {
  return request({
    url: '/teach/parent/export',
    method: 'post',
    data: query,
    responseType: 'blob'
  })
}

// Query students under a parent
export function getParentChildren(parentId) {
  return request({
    url: '/teach/student/parent/' + parentId,
    method: 'get'
  })
}
