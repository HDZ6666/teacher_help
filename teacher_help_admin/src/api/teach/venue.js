import request from '@/utils/request'

// ======================== 场馆 ========================
export function listVenue(query) {
  return request({ url: '/teach/venue/list', method: 'get', params: query })
}

export function getVenue(venueId) {
  return request({ url: '/teach/venue/' + venueId, method: 'get' })
}

export function addVenue(data) {
  return request({ url: '/teach/venue', method: 'post', data: data })
}

export function updateVenue(data) {
  return request({ url: '/teach/venue', method: 'put', data: data })
}

export function changeVenueStatus(data) {
  return request({ url: '/teach/venue/changeStatus', method: 'put', data: data })
}

export function delVenue(venueIds) {
  return request({ url: '/teach/venue/' + venueIds, method: 'delete' })
}

// ======================== 场地（含可约时段、分时价格规则） ========================
export function listCourt(query) {
  return request({ url: '/teach/venue/court/list', method: 'get', params: query })
}

export function getCourt(courtId) {
  return request({ url: '/teach/venue/court/' + courtId, method: 'get' })
}

export function addCourt(data) {
  return request({ url: '/teach/venue/court', method: 'post', data: data })
}

export function updateCourt(data) {
  return request({ url: '/teach/venue/court', method: 'put', data: data })
}

export function delCourt(courtIds) {
  return request({ url: '/teach/venue/court/' + courtIds, method: 'delete' })
}

// ======================== 订场 / 预订 ========================
// 订场日历（某场馆某日各场地的可约时段与占用）
export function getBookingGrid(query) {
  return request({ url: '/teach/venue/booking/grid', method: 'get', params: query })
}

// 预订报价（后端按场地价格与分时规则计算）
export function getBookingQuote(query) {
  return request({ url: '/teach/venue/booking/quote', method: 'get', params: query })
}

export function listBooking(query) {
  return request({ url: '/teach/venue/booking/list', method: 'get', params: query })
}

export function getBooking(bookingId) {
  return request({ url: '/teach/venue/booking/' + bookingId, method: 'get' })
}

// 代预订
export function addBooking(data) {
  return request({ url: '/teach/venue/booking', method: 'post', data: data })
}

// 锁场（单日或日期范围/星期/多场地批量）
export function lockCourt(data) {
  return request({ url: '/teach/venue/booking/lock', method: 'post', data: data })
}

// 按批次解除锁场
export function cancelLockGroup(data) {
  return request({ url: '/teach/venue/booking/lock/cancel', method: 'put', data: data })
}

// 核销
export function verifyBooking(data) {
  return request({ url: '/teach/venue/booking/verify', method: 'put', data: data })
}

// 取消（可退款）
export function cancelBooking(data) {
  return request({ url: '/teach/venue/booking/cancel', method: 'put', data: data })
}
