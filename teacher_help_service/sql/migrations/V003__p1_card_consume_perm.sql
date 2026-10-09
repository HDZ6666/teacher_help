-- ----------------------------
-- V003 会员卡核销按钮权限（P1）
-- 新接口 PUT /teach/card/grant/consume 使用权限标识 teach:card:consume。
-- 菜单ID 5900 为固定ID（见 sql/gen_teach_sql.py 中 PINNED_BUTTON_IDS），与 sql/teacher_help_menu.sql 一致，可重复执行。
-- 父菜单 5009 为“会员卡管理”权限目录（由 sql/teacher_help_menu.sql 创建）。
-- 执行后非超管角色需在“角色管理”中勾选“会员卡管理核销”。
-- ----------------------------
insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5900, '会员卡管理核销', 5009, 7, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:card:consume', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
