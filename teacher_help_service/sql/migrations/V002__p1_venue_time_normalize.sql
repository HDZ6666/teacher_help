-- ----------------------------
-- V002 场地时段统一为补零的 HH:MM（P1）
-- 原因：旧代码以字符串比较时间，'9:00' >= '10:00' 为真，冲突校验和订场日历会误判。
-- 新代码写入前统一规范为 HH:MM，这里把存量数据一并修正，修正后字符串字典序即时间先后。
-- 执行前可先查看受影响行数：
--   SELECT COUNT(*) FROM teach_court_time WHERE start_time NOT REGEXP '^[0-9]{2}:[0-9]{2}$' OR end_time NOT REGEXP '^[0-9]{2}:[0-9]{2}$';
--   SELECT COUNT(*) FROM teach_court_booking WHERE start_time NOT REGEXP '^[0-9]{2}:[0-9]{2}$' OR end_time NOT REGEXP '^[0-9]{2}:[0-9]{2}$';
-- ----------------------------

-- 去掉秒：HH:MM:SS -> HH:MM
UPDATE teach_court_time SET start_time = LEFT(start_time, 5) WHERE start_time REGEXP '^[0-9]{2}:[0-9]{2}:[0-9]{2}$';
UPDATE teach_court_time SET end_time = LEFT(end_time, 5) WHERE end_time REGEXP '^[0-9]{2}:[0-9]{2}:[0-9]{2}$';
UPDATE teach_court_booking SET start_time = LEFT(start_time, 5) WHERE start_time REGEXP '^[0-9]{2}:[0-9]{2}:[0-9]{2}$';
UPDATE teach_court_booking SET end_time = LEFT(end_time, 5) WHERE end_time REGEXP '^[0-9]{2}:[0-9]{2}:[0-9]{2}$';

-- 小时补零：H:MM / H:MM:SS -> 0H:MM
UPDATE teach_court_time SET start_time = CONCAT('0', LEFT(start_time, 4)) WHERE start_time REGEXP '^[0-9]:[0-9]{2}(:[0-9]{2})?$';
UPDATE teach_court_time SET end_time = CONCAT('0', LEFT(end_time, 4)) WHERE end_time REGEXP '^[0-9]:[0-9]{2}(:[0-9]{2})?$';
UPDATE teach_court_booking SET start_time = CONCAT('0', LEFT(start_time, 4)) WHERE start_time REGEXP '^[0-9]:[0-9]{2}(:[0-9]{2})?$';
UPDATE teach_court_booking SET end_time = CONCAT('0', LEFT(end_time, 4)) WHERE end_time REGEXP '^[0-9]:[0-9]{2}(:[0-9]{2})?$';
