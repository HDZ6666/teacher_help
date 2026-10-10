-- ----------------------------
-- V012 P3 第二批：费用导入、老师权限配置
-- 1. 新增按钮权限（固定菜单ID，见 sql/gen_teach_sql.py PINNED_BUTTON_IDS）：
--    5918 ast:fee:import（费用导入：POST /ast/inventory/fee/import/template、/ast/inventory/fee/import）
--    5919 teach:teacher:permission（老师权限：/teach/teacher-permission/*，为角色勾选“老师帮业务权限”下的菜单与按钮）
-- 2. 本迁移不改表结构；销售订单详情 GET /ast/inventory/sale-order/{orderId} 复用已有 ast:inventory:query / ast:item:query 权限。
-- 注意：teach:teacher:permission 可以给任意非超级管理员角色分配业务权限（含其本身），只应授予机构管理员。
-- 回退：DELETE FROM sys_role_menu WHERE menu_id IN (5918, 5919); DELETE FROM sys_menu WHERE menu_id IN (5918, 5919);
-- ----------------------------

insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5919, '老师管理老师权限配置', 5003, 7, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:teacher:permission', '#', 'admin', sysdate(), '', null, ''),
(5918, '费用管理导入', 5015, 6, '#', null, null, '', 1, 0, 'F', '0', '0', 'ast:fee:import', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
