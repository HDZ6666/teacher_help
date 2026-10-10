import request from '@/utils/request'

// 角色列表（含已授权的业务按钮数）
export function listPermissionRoles() {
  return request({ url: '/teach/teacher-permission/roles', method: 'get' })
}

// 角色的业务权限树与已勾选项
export function getRolePermission(roleId) {
  return request({ url: '/teach/teacher-permission/role/' + roleId, method: 'get' })
}

// 保存角色业务权限（只影响“老师帮业务权限”下的菜单）
export function saveRolePermission(data) {
  return request({ url: '/teach/teacher-permission/role', method: 'put', data })
}
