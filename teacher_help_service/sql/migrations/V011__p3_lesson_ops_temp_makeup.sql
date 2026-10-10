-- ----------------------------
-- V011 P3 第二批：课表内联点名/调课/临时学员、按周重复排课、修改单个学员点名、编辑课次、开补课班
-- 1. teach_schedule_attendances 新增：is_temp（临时学员/补课学员，不在班级在读名单内，只加入单个课次）、
--    course_account_id（临时学员扣课课程账户）、makeup_detail_id（开补课班时指向原缺课点名明细）。
-- 2. teach_schedule_events 新增 event_type（normal=常规 makeup=补课班），存量数据默认 normal。
-- 3. teach_class_attendance_detail 新增 is_temp（临时学员点名）、makeup_source_id（补课课次点名时指向原缺课明细）。
-- 4. teach_course_account_log.op_type 新增取值 attendance_edit=修改点名（列类型与库注释不变，仅代码取值）。
-- 5. 新增按钮权限（固定菜单ID，见 sql/gen_teach_sql.py PINNED_BUTTON_IDS）：
--    5912 teach:schedule:event:reschedule  5913 teach:schedule:event:temp  5914 teach:schedule:event:batch
--    5915 teach:classRecord:editDetail     5916 teach:classRecord:edit     5917 teach:classRecord:makeupClass
-- 部署前必须先执行本迁移：新代码读写课次名单与点名明细的新增字段。
-- 回退（确认未使用后）：ALTER TABLE teach_class_attendance_detail DROP COLUMN makeup_source_id, DROP COLUMN is_temp;
--   ALTER TABLE teach_schedule_events DROP COLUMN event_type;
--   ALTER TABLE teach_schedule_attendances DROP COLUMN makeup_detail_id, DROP COLUMN course_account_id, DROP COLUMN is_temp;
--   DELETE FROM sys_menu WHERE menu_id BETWEEN 5912 AND 5917;
-- ----------------------------

ALTER TABLE teach_schedule_attendances ADD COLUMN is_temp SMALLINT NOT NULL DEFAULT 0 COMMENT '是否临时学员（0否 1是）' AFTER is_countable;

ALTER TABLE teach_schedule_attendances ADD COLUMN course_account_id INT NULL COMMENT '临时学员扣课课程账户ID' AFTER is_temp;

ALTER TABLE teach_schedule_attendances ADD COLUMN makeup_detail_id INT NULL COMMENT '补课来源点名明细ID（开补课班生成）' AFTER course_account_id;

CREATE INDEX idx_schedule_attendance_makeup ON teach_schedule_attendances (makeup_detail_id);

ALTER TABLE teach_schedule_events ADD COLUMN event_type VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '课次类型（normal常规 makeup补课）' AFTER status;

ALTER TABLE teach_class_attendance_detail ADD COLUMN is_temp SMALLINT NOT NULL DEFAULT 0 COMMENT '是否临时学员(0=否 1=是)' AFTER makeup_remark;

ALTER TABLE teach_class_attendance_detail ADD COLUMN makeup_source_id INT NULL COMMENT '补课来源点名明细ID' AFTER is_temp;

insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5914, '排课管理按周重复排课', 5006, 6, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:schedule:event:batch', '#', 'admin', sysdate(), '', null, ''),
(5912, '排课管理调课', 5006, 8, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:schedule:event:reschedule', '#', 'admin', sysdate(), '', null, ''),
(5913, '排课管理临时学员', 5006, 9, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:schedule:event:temp', '#', 'admin', sysdate(), '', null, ''),
(5916, '上课记录修改', 5008, 3, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:classRecord:edit', '#', 'admin', sysdate(), '', null, ''),
(5915, '上课记录修改单个学员点名', 5008, 4, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:classRecord:editDetail', '#', 'admin', sysdate(), '', null, ''),
(5917, '上课记录开补课班', 5008, 7, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:classRecord:makeupClass', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
