import request from '@/utils/request'

// 批量升班
export function promoteClasses(data) {
  return request({ url: '/teach/class-batch/promote', method: 'post', data, timeout: 60000 })
}

// 批量结业
export function graduateClasses(data) {
  return request({ url: '/teach/class-batch/graduate', method: 'post', data, timeout: 60000 })
}
