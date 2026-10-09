-- ============================================================================
-- 数据修正：存量学员 status='1' 核对与回填（P1，人工执行，不在 migrate.py 中自动运行）
--
-- 背景：P0 之前 PC 端“新建学员”把“在读”按前端口径传为 '1'，而后端口径是
--       0在读 1休学 2转学 3毕业，因此这批学员在库里显示为“休学”。
--       P0（refactor/v2）已统一口径，新数据不再受影响；本脚本只处理存量数据。
--
-- 无法 100% 自动区分“真休学”与“被写错的在读”，因此分三步：
--   第 1 步：只读核对（可反复执行）
--   第 2 步：备份
--   第 3 步：按人工确认的学员ID回填（带多重保护条件，默认不会改动任何数据）
-- 执行环境：MySQL 8.x；请先在测试库演练，并在业务低峰执行。
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 第 1 步：核对查询（只读）
-- suspected_reason 说明：
--   has_active_account   有有效课程账户且剩余课时 > 0
--   in_active_class      仍在某个班级的在读名单中
--   attended_recently    近 90 天有到课/迟到记录
-- 同时满足多项的，基本可以判定为“被写错的在读”；三项都没有的，请与校区确认是否真休学。
-- 如已知修复上线日期，可把 create_time 条件改为 < '<P0 上线时间>' 进一步缩小范围。
-- ----------------------------------------------------------------------------
SELECT
  s.id,
  s.student_name,
  s.status,
  s.create_by,
  s.create_time,
  s.update_time,
  EXISTS (
    SELECT 1 FROM teach_student_course_account a
    WHERE a.student_id = s.id AND a.del_flag = 0 AND a.status = 'active' AND a.remaining_quantity > 0
  ) AS has_active_account,
  EXISTS (
    SELECT 1 FROM teach_class_student cs
    WHERE cs.student_id = s.id AND cs.del_flag = 0 AND cs.status = 1
  ) AS in_active_class,
  EXISTS (
    SELECT 1 FROM teach_class_attendance_detail d
    JOIN teach_class_attendance att ON att.id = d.attendance_id AND att.del_flag = 0
    WHERE d.student_id = s.id AND d.del_flag = 0 AND d.status IN (1, 2)
      AND att.class_date >= CURDATE() - INTERVAL 90 DAY
  ) AS attended_recently
FROM teach_students s
WHERE s.del_flag = '0'
  AND s.status = '1'
ORDER BY s.create_time DESC;


-- ----------------------------------------------------------------------------
-- 第 2 步：备份（执行一次即可；表已存在时会报错，说明之前已经备份过）
-- ----------------------------------------------------------------------------
CREATE TABLE bak_20261009_teach_students_status AS
SELECT id, student_name, status, update_by, update_time, NOW() AS backup_time
FROM teach_students
WHERE del_flag = '0' AND status = '1';


-- ----------------------------------------------------------------------------
-- 第 3 步：按人工确认的ID回填为在读（'0'）
-- 1. 把第 1 步核对后确认要回填的学员ID填入 IN (...)，默认 -1 表示不修改任何数据；
-- 2. 只会修改 status 仍为 '1'、且已在备份表中的学员；
-- 3. 先执行 SELECT 预览，确认行数后再执行 UPDATE，最后 COMMIT；有疑问时 ROLLBACK。
-- ----------------------------------------------------------------------------
START TRANSACTION;

SELECT s.id, s.student_name, s.status
FROM teach_students s
JOIN bak_20261009_teach_students_status b ON b.id = s.id
WHERE s.del_flag = '0'
  AND s.status = '1'
  AND s.id IN (-1);

UPDATE teach_students s
JOIN bak_20261009_teach_students_status b ON b.id = s.id
SET s.status = '0',
    s.update_by = 'data_fix_20261009',
    s.update_time = NOW()
WHERE s.del_flag = '0'
  AND s.status = '1'
  AND s.id IN (-1);

-- 确认无误后执行 COMMIT；否则执行 ROLLBACK
-- COMMIT;
-- ROLLBACK;


-- ----------------------------------------------------------------------------
-- 回退（如需）：按备份恢复第 3 步修改过的学员
-- UPDATE teach_students s
-- JOIN bak_20261009_teach_students_status b ON b.id = s.id
-- SET s.status = b.status, s.update_by = b.update_by, s.update_time = b.update_time
-- WHERE s.update_by = 'data_fix_20261009';
-- ----------------------------------------------------------------------------
