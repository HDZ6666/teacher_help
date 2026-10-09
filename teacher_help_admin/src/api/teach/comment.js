import request from '@/utils/request'

// 查询课后点评列表
export function listComment(query) {
  return request({
    url: '/teach/comment/list',
    method: 'get',
    params: query
  })
}

// 查询某次点名下未点评学员
export function listPendingCommentStudents(attendanceId) {
  return request({
    url: '/teach/comment/pending',
    method: 'get',
    params: { attendance_id: attendanceId }
  })
}

// 查询课后点评详细
export function getComment(commentId) {
  return request({
    url: '/teach/comment/' + commentId,
    method: 'get'
  })
}

// 发布点评（单个学员）
export function addComment(data) {
  return request({
    url: '/teach/comment',
    method: 'post',
    data: data
  })
}

// 批量/统一点评（一组学员同一内容）
export function batchComment(data) {
  return request({
    url: '/teach/comment/batch',
    method: 'post',
    data: data
  })
}

// 修改点评
export function updateComment(data) {
  return request({
    url: '/teach/comment',
    method: 'put',
    data: data
  })
}

// 撤销点评
export function delComment(commentIds) {
  return request({
    url: '/teach/comment/' + commentIds,
    method: 'delete'
  })
}
