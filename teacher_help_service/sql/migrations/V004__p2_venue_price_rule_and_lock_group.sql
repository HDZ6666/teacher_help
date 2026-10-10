-- ----------------------------
-- V004 场地分时价格规则 + 批量锁场批次号（P2）
-- 1. 新增 teach_court_price_rule：按星期 + 时段覆盖场地默认价格（未覆盖的时段仍用 teach_court 的默认价格）
-- 2. teach_court_booking 新增 lock_group_no：同一次“日期范围/多场地”批量锁场共用一个批次号，可按批次解除
-- 均为新增结构，不修改存量数据；没有配置价格规则的场地计费结果与 P1 完全一致。
-- 回退（确认未使用后）：DROP TABLE teach_court_price_rule; ALTER TABLE teach_court_booking DROP INDEX idx_court_booking_lock_group, DROP COLUMN lock_group_no;
-- ----------------------------

CREATE TABLE IF NOT EXISTS teach_court_price_rule (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  court_id INTEGER NOT NULL COMMENT '场地ID',
  week_day SMALLINT NOT NULL COMMENT '星期(1-7)',
  start_time VARCHAR(10) NOT NULL COMMENT '开始时间(HH:MM)',
  end_time VARCHAR(10) NOT NULL COMMENT '结束时间(HH:MM)',
  price_per_hour DECIMAL(10, 2) COMMENT '该时段每小时价格',
  price_per_half_hour DECIMAL(10, 2) COMMENT '该时段每半小时价格',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_court_price_rule_court (court_id, week_day),
  FOREIGN KEY(court_id) REFERENCES teach_court (id)
) ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='场地分时价格规则表';

ALTER TABLE teach_court_booking ADD COLUMN lock_group_no VARCHAR(50) NULL COMMENT '批量锁场批次号' AFTER booking_type;

ALTER TABLE teach_court_booking ADD INDEX idx_court_booking_lock_group (lock_group_no);
