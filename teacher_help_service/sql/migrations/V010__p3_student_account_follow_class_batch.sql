-- ----------------------------
-- V010 P3 学员报读与班级批量操作
-- 1. teach_student_course_account 新增：cleared_quantity（课时清零/结课清零数量）、stop_date / planned_resume_date / stop_reason（停课）、
--    complete_date（结课/转出日期）；status 新增取值 transferred=已转出（列类型不变，仅注释与取值）。
-- 2. 新表 teach_course_account_log：课程账户操作日志（转课/清零/改有效期/停课/复课/结课/导入）。
-- 3. 新表 teach_student_follow：学员跟进记录。
-- 4. 新增按钮权限（固定菜单ID，见 sql/gen_teach_sql.py PINNED_BUTTON_IDS）：
--    5906 teach:student:import  5907 teach:student:follow  5908 teach:student:account
--    5909 teach:class:import    5910 teach:class:promote   5911 teach:class:graduate
-- 部署前必须先执行本迁移：新代码查询课程账户会读取新增字段。
-- 回退（确认未使用后）：DROP TABLE teach_student_follow; DROP TABLE teach_course_account_log;
--   ALTER TABLE teach_student_course_account DROP COLUMN complete_date, DROP COLUMN stop_reason,
--   DROP COLUMN planned_resume_date, DROP COLUMN stop_date, DROP COLUMN cleared_quantity;
--   DELETE FROM sys_menu WHERE menu_id BETWEEN 5906 AND 5911;
-- ----------------------------

ALTER TABLE teach_student_course_account ADD COLUMN cleared_quantity INT NOT NULL DEFAULT 0 COMMENT '已清零数量' AFTER remaining_quantity;

ALTER TABLE teach_student_course_account ADD COLUMN stop_date DATE NULL COMMENT '停课日期' AFTER status;

ALTER TABLE teach_student_course_account ADD COLUMN planned_resume_date DATE NULL COMMENT '计划复课日期(仅记录，需手动复课)' AFTER stop_date;

ALTER TABLE teach_student_course_account ADD COLUMN stop_reason VARCHAR(100) NULL COMMENT '停课原因' AFTER planned_resume_date;

ALTER TABLE teach_student_course_account ADD COLUMN complete_date DATE NULL COMMENT '结课/转出日期' AFTER stop_reason;

CREATE TABLE IF NOT EXISTS teach_course_account_log (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  batch_no VARCHAR(50) NOT NULL COMMENT '操作批次号',
  op_type VARCHAR(20) NOT NULL COMMENT '操作类型(transfer_out=转出 transfer_in=转入 clear=课时清零 validity=改有效期 stop=停课 resume=复课 complete=结课 import=导入)',
  account_id INTEGER NOT NULL COMMENT '课程账户ID',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) COMMENT '学员姓名快照',
  course_id INTEGER COMMENT '课程ID',
  course_name VARCHAR(100) COMMENT '课程名称快照',
  change_quantity INTEGER NOT NULL COMMENT '变动数量(减少为负)',
  before_remaining INTEGER COMMENT '变动前剩余',
  after_remaining INTEGER COMMENT '变动后剩余',
  before_status VARCHAR(20) COMMENT '变动前状态',
  after_status VARCHAR(20) COMMENT '变动后状态',
  before_valid_start DATE COMMENT '变动前有效期开始',
  before_valid_end DATE COMMENT '变动前有效期结束',
  after_valid_start DATE COMMENT '变动后有效期开始',
  after_valid_end DATE COMMENT '变动后有效期结束',
  related_account_id INTEGER COMMENT '关联课程账户ID(转课对方账户)',
  related_order_id INTEGER COMMENT '关联订单ID',
  reason VARCHAR(200) COMMENT '原因/备注',
  create_by VARCHAR(64) COMMENT '操作人',
  create_time DATETIME COMMENT '操作时间',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='学员课程账户操作日志表（P3：转课/课时清零/改有效期/停课/复课/结课/导入）';

CREATE TABLE IF NOT EXISTS teach_student_follow (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) COMMENT '学员姓名快照',
  follow_type VARCHAR(20) NOT NULL COMMENT '跟进方式(phone=电话 wechat=微信 visit=面谈 other=其他)',
  follow_stage VARCHAR(50) COMMENT '跟进阶段',
  content TEXT NOT NULL COMMENT '跟进内容',
  follow_time DATETIME NOT NULL COMMENT '跟进时间',
  next_follow_date DATE COMMENT '下次跟进日期',
  follow_user_id INTEGER COMMENT '跟进人(sys_user.user_id)',
  follow_user_name VARCHAR(64) COMMENT '跟进人姓名快照',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='学员跟进记录表（P3）';

CREATE INDEX idx_course_account_log_account ON teach_course_account_log (account_id);

CREATE INDEX idx_course_account_log_student ON teach_course_account_log (student_id);

CREATE INDEX idx_student_follow_student ON teach_student_follow (student_id);

insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) values
(5906, '学员管理导入', 5001, 10, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:student:import', '#', 'admin', sysdate(), '', null, ''),
(5907, '学员管理跟进记录', 5001, 9, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:student:follow', '#', 'admin', sysdate(), '', null, ''),
(5908, '学员管理报读课程变更（转课/清零/有效期/停复结课）', 5001, 7, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:student:account', '#', 'admin', sysdate(), '', null, ''),
(5909, '班级管理导入', 5004, 7, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:class:import', '#', 'admin', sysdate(), '', null, ''),
(5910, '班级管理批量升班', 5004, 8, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:class:promote', '#', 'admin', sysdate(), '', null, ''),
(5911, '班级管理批量结业', 5004, 6, '#', null, null, '', 1, 0, 'F', '0', '0', 'teach:class:graduate', '#', 'admin', sysdate(), '', null, '')
on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), order_num = values(order_num), perms = values(perms), remark = values(remark);
