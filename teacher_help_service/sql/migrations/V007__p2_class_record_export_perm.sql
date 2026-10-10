-- ----------------------------
-- V007 上课记录导出按钮权限（P2）
-- 新接口 POST /teach/class-record/{attendance|overtime|makeup|absence}/export 使用权限标识 teach:classRecord:export。
-- 菜单ID 5903 为固定ID（见 sql/gen_teach_sql.py 中 PINNED_BUTTON_IDS），与 sql/teacher_help_menu.sql 一致，可重复执行。
-- 父菜单 5008 为“上课记录”权限目录（由 sql/teacher_help_menu.sql 创建）。
-- ----------------------------
insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5903, '上课记录导出', 5008, 3, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:classRecord:export', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
