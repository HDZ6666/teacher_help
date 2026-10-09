import request from '@/utils/request'

// ------------------------ 卡类型（卡模板） ------------------------
// 查询会员卡列表
export function listCard(query) {
  return request({
    url: '/teach/card/list',
    method: 'get',
    params: query
  })
}

// 查询会员卡详细（含适用课程）
export function getCard(cardId) {
  return request({
    url: '/teach/card/' + cardId,
    method: 'get'
  })
}

// 新增会员卡
export function addCard(data) {
  return request({
    url: '/teach/card',
    method: 'post',
    data: data
  })
}

// 修改会员卡
export function updateCard(data) {
  return request({
    url: '/teach/card',
    method: 'put',
    data: data
  })
}

// 启用/停用会员卡
export function changeCardStatus(data) {
  return request({
    url: '/teach/card/changeStatus',
    method: 'put',
    data: data
  })
}

// 删除会员卡
export function delCard(cardIds) {
  return request({
    url: '/teach/card/' + cardIds,
    method: 'delete'
  })
}

// ------------------------ 发放 / 核销 / 作废 ------------------------
// 查询发放记录
export function listCardGrant(query) {
  return request({
    url: '/teach/card/grant/list',
    method: 'get',
    params: query
  })
}

// 发卡给学员
export function grantCard(data) {
  return request({
    url: '/teach/card/grant',
    method: 'post',
    data: data
  })
}

// 核销（消耗次数）
export function consumeCardGrant(data) {
  return request({
    url: '/teach/card/grant/consume',
    method: 'put',
    data: data
  })
}

// 作废发放记录
export function voidCardGrant(data) {
  return request({
    url: '/teach/card/grant/void',
    method: 'put',
    data: data
  })
}

// 查询学员持有的会员卡
export function listStudentCards(studentId) {
  return request({
    url: '/teach/card/student/' + studentId,
    method: 'get'
  })
}

// ------------------------ 操作记录 ------------------------
export function listCardLog(query) {
  return request({
    url: '/teach/card/log/list',
    method: 'get',
    params: query
  })
}
