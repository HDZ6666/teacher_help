-- ----------------------------
-- V008 缺课补课“标记已补”（P2）
-- 1. teach_class_attendance_detail 新增补课标记字段：只记录补课标记/时间/操作人/说明，不影响扣课与课程账户，存量数据默认 0=未补。
-- 2. 新增按钮权限 teach:classRecord:makeup（固定菜单ID 5904，见 sql/gen_teach_sql.py 中 PINNED_BUTTON_IDS），对应 PUT /teach/class-record/makeup/mark。
-- 回退（确认未使用后）：ALTER TABLE teach_class_attendance_detail DROP COLUMN makeup_remark, DROP COLUMN makeup_by, DROP COLUMN makeup_time, DROP COLUMN makeup_flag; DELETE FROM sys_menu WHERE menu_id = 5904;
-- ----------------------------

ALTER TABLE teach_class_attendance_detail ADD COLUMN makeup_flag SMALLINT NOT NULL DEFAULT 0 COMMENT '补课标记(0=未补 1=已补)' AFTER consume_method;

ALTER TABLE teach_class_attendance_detail ADD COLUMN makeup_time DATETIME NULL COMMENT '标记已补时间' AFTER makeup_flag;

ALTER TABLE teach_class_attendance_detail ADD COLUMN makeup_by VARCHAR(64) NULL COMMENT '标记已补操作人' AFTER makeup_time;

ALTER TABLE teach_class_attendance_detail ADD COLUMN makeup_remark VARCHAR(200) NULL COMMENT '补课说明' AFTER makeup_by;

insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5904, '上课记录标记已补', 5008, 4, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:classRecord:makeup', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
