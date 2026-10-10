from sqlalchemy import text
from config.env import DataBaseConfig
from utils.log_util import logger


async def patch_teach_schedule_schema(conn):
    """
    Backfill schedule columns required by the PC timetable prototype.
    """
    if DataBaseConfig.db_type != 'mysql':
        return

    async def has_column(table_name: str, column_name: str):
        result = await conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table_name
                  AND COLUMN_NAME = :column_name
                """
            ),
            {'table_name': table_name, 'column_name': column_name},
        )
        return (result.scalar() or 0) > 0

    async def add_column_if_missing(table_name: str, column_name: str, column_sql: str):
        if await has_column(table_name, column_name):
            return
        await conn.execute(text(f'ALTER TABLE `{table_name}` ADD COLUMN {column_sql}'))
        logger.info(f'已补齐字段 {table_name}.{column_name}')

    await add_column_if_missing(
        'teach_schedule_events',
        'course_id',
        "`course_id` INT NULL COMMENT '课程ID' AFTER `teacher_id`",
    )
    await add_column_if_missing(
        'teach_schedule_events',
        'course_name',
        "`course_name` VARCHAR(100) NULL COMMENT '课程名称快照' AFTER `course_id`",
    )
    await add_column_if_missing(
        'teach_schedule_events',
        'class_id',
        "`class_id` INT NULL COMMENT '班级ID' AFTER `course_name`",
    )
    await add_column_if_missing(
        'teach_schedule_events',
        'class_name',
        "`class_name` VARCHAR(100) NULL COMMENT '班级名称快照' AFTER `class_id`",
    )
    await add_column_if_missing(
        'teach_schedule_events',
        'classroom',
        "`classroom` VARCHAR(100) NULL COMMENT '上课教室' AFTER `event_date`",
    )
    await add_column_if_missing(
        'teach_schedule_events',
        'lesson_hours',
        "`lesson_hours` DECIMAL(6,2) NULL DEFAULT 1.00 COMMENT '授课课时' AFTER `classroom`",
    )
    await add_column_if_missing(
        'teach_schedule_events',
        'content',
        "`content` VARCHAR(500) NULL COMMENT '上课内容' AFTER `lesson_hours`",
    )
    await add_column_if_missing(
        'teach_class_attendance',
        'event_id',
        "`event_id` INT NULL COMMENT '排课事件ID' AFTER `id`",
    )
    await add_column_if_missing(
        'teach_court_booking',
        'lock_group_no',
        "`lock_group_no` VARCHAR(50) NULL COMMENT '批量锁场批次号' AFTER `booking_type`",
    )
