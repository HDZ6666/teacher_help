import request from '@/utils/request'

// 查询排课事件列表
export function listScheduleEvent(query) {
  return request({
    url: '/teach/schedule/event/list',
    method: 'get',
    params: query
  })
}

// 查询排课事件详细
export function getScheduleEvent(eventId) {
  return request({
    url: '/teach/schedule/event/' + eventId,
    method: 'get'
  })
}

// 新增排课事件
export function addScheduleEvent(data) {
  return request({
    url: '/teach/schedule/event',
    method: 'post',
    data: data
  })
}

// 修改排课事件
export function updateScheduleEvent(data) {
  return request({
    url: '/teach/schedule/event',
    method: 'put',
    data: data
  })
}

// 删除排课事件
export function delScheduleEvent(eventIds) {
  return request({
    url: '/teach/schedule/event/' + eventIds,
    method: 'delete'
  })
}

// 获取日历事件数据（FullCalendar格式）
export function getCalendarEvents(query) {
  return request({
    url: '/teach/schedule/event/calendar/events',
    method: 'get',
    params: query
  })
}

// 导出排课
export function exportScheduleEvent(query) {
  return request({
    url: '/teach/schedule/event/export',
    method: 'get',
    params: query
  })
}

