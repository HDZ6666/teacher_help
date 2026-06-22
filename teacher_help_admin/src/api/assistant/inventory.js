import request from '@/utils/request'

// 物品管理
export function listItem(query) {
  return request({
    url: '/ast/item/list',
    method: 'get',
    params: query
  })
}

export function getItem(itemId) {
  return request({
    url: '/ast/item/' + itemId,
    method: 'get'
  })
}

export function addItem(data) {
  return request({
    url: '/ast/item',
    method: 'post',
    data
  })
}

export function updateItem(data) {
  return request({
    url: '/ast/item',
    method: 'put',
    data
  })
}

export function delItem(itemIds) {
  return request({
    url: '/ast/item/' + itemIds,
    method: 'delete'
  })
}

export function listItemSku(itemId) {
  return request({
    url: '/ast/inventory/item/' + itemId + '/skus',
    method: 'get'
  })
}

export function listAvailableItems(query) {
  return request({
    url: '/ast/inventory/items/options',
    method: 'get',
    params: query
  })
}

export function listRoleOptions(query) {
  return request({
    url: '/ast/inventory/role-options',
    method: 'get',
    params: query
  })
}

// 出入库管理
export function listStockRecord(query) {
  return request({
    url: '/ast/inventory/stock/list',
    method: 'get',
    params: query
  })
}

export function getStockRecord(recordId) {
  return request({
    url: '/ast/inventory/stock/' + recordId,
    method: 'get'
  })
}

export function voidStockRecord(recordId) {
  return request({
    url: '/ast/inventory/stock/' + recordId + '/void',
    method: 'put'
  })
}

export function createPurchase(data) {
  return request({
    url: '/ast/inventory/purchase',
    method: 'post',
    data
  })
}

export function importPurchase(data) {
  return request({
    url: '/ast/inventory/purchase/import',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data',
      repeatSubmit: false
    }
  })
}

export function createReceive(data) {
  return request({
    url: '/ast/inventory/receive',
    method: 'post',
    data
  })
}

export function createReturn(data) {
  return request({
    url: '/ast/inventory/return',
    method: 'post',
    data
  })
}

export function createInventory(data) {
  return request({
    url: '/ast/inventory/inventory',
    method: 'post',
    data
  })
}

// 费用管理
export function listFee(query) {
  return request({
    url: '/ast/inventory/fee/list',
    method: 'get',
    params: query
  })
}

export function getFee(feeId) {
  return request({
    url: '/ast/inventory/fee/' + feeId,
    method: 'get'
  })
}

export function addFee(data) {
  return request({
    url: '/ast/inventory/fee',
    method: 'post',
    data
  })
}

export function updateFee(data) {
  return request({
    url: '/ast/inventory/fee',
    method: 'put',
    data
  })
}

export function changeFeeStatus(data) {
  return request({
    url: '/ast/inventory/fee/changeStatus',
    method: 'put',
    data
  })
}

export function delFee(feeIds) {
  return request({
    url: '/ast/inventory/fee/' + feeIds,
    method: 'delete'
  })
}
