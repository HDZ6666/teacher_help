-- ----------------------------
-- V009 学员跟进人/学管师持久化（P2）
-- 1. teach_students 新增 follower_user_id / advisor_user_id（系统员工账号 sys_user.user_id，空=待分配），存量学员均为待分配。
-- 2. 新增按钮权限 teach:student:assign（固定菜单ID 5905，见 sql/gen_teach_sql.py 中 PINNED_BUTTON_IDS），
--    对应 GET /teach/student/staff-options 与 PUT /teach/student/assign。父菜单 5001 为“学员管理”权限目录。
-- 回退（确认未使用后）：ALTER TABLE teach_students DROP COLUMN advisor_user_id, DROP COLUMN follower_user_id; DELETE FROM sys_menu WHERE menu_id = 5905;
-- ----------------------------

ALTER TABLE teach_students ADD COLUMN follower_user_id INT NULL COMMENT '跟进人(sys_user.user_id)' AFTER status;

ALTER TABLE teach_students ADD COLUMN advisor_user_id INT NULL COMMENT '学管师(sys_user.user_id)' AFTER follower_user_id;

insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5905, '学员管理分配跟进人/学管师', 5001, 7, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:student:assign', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
