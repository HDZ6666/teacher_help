from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.entity.do.teach_class_do import TeachClassAttendance, TeachClassAttendanceDetail
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent


class TeachLessonDao:
    """
    课次操作（调课/临时学员/按周排课/修改单个点名/编辑课次/开补课班）数据库操作层
    """

    @classmethod
    async def get_roster_row(cls, db: AsyncSession, event_id: int, student_id: int):
        result = await db.execute(
            select(TeachScheduleAttendance).where(
                TeachScheduleAttendance.event_id == event_id,
                TeachScheduleAttendance.student_id == student_id,
                TeachScheduleAttendance.del_flag == '0',
            )
        )
        return result.scalars().first()

    @classmethod
    async def get_detail_for_update(cls, db: AsyncSession, detail_id: int):
        await db.flush()
        result = await db.execute(
            select(TeachClassAttendanceDetail)
            .where(TeachClassAttendanceDetail.id == detail_id, TeachClassAttendanceDetail.del_flag == 0)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalars().first()

    @classmethod
    async def get_detail(cls, db: AsyncSession, detail_id: int):
        result = await db.execute(
            select(TeachClassAttendanceDetail).where(
                TeachClassAttendanceDetail.id == detail_id, TeachClassAttendanceDetail.del_flag == 0
            )
        )
        return result.scalars().first()

    @classmethod
    async def get_active_details(cls, db: AsyncSession, attendance_id: int):
        result = await db.execute(
            select(TeachClassAttendanceDetail).where(
                TeachClassAttendanceDetail.attendance_id == attendance_id,
                TeachClassAttendanceDetail.del_flag == 0,
            )
        )
        return result.scalars().all()

    @classmethod
    async def get_absence_details_with_attendance(cls, db: AsyncSession, detail_ids: list[int]):
        """
        缺课记录（点名明细）及所属点名记录，按明细ID升序加锁
        """
        await db.flush()
        result = await db.execute(
            select(TeachClassAttendanceDetail, TeachClassAttendance)
            .join(TeachClassAttendance, TeachClassAttendanceDetail.attendance_id == TeachClassAttendance.id)
            .where(
                TeachClassAttendanceDetail.id.in_(detail_ids),
                TeachClassAttendanceDetail.del_flag == 0,
                TeachClassAttendance.del_flag == 0,
            )
            .order_by(TeachClassAttendanceDetail.id)
            .with_for_update(of=TeachClassAttendanceDetail)
            .execution_options(populate_existing=True)
        )
        return result.all()

    @classmethod
    async def get_pending_makeup_rows(cls, db: AsyncSession, detail_ids: list[int]):
        """
        已安排在未取消、未删除补课课次中的缺课记录
        """
        result = await db.execute(
            select(TeachScheduleAttendance.makeup_detail_id, TeachScheduleEvent.id, TeachScheduleEvent.start_time)
            .join(TeachScheduleEvent, TeachScheduleAttendance.event_id == TeachScheduleEvent.id)
            .where(
                TeachScheduleAttendance.makeup_detail_id.in_(detail_ids),
                TeachScheduleAttendance.del_flag == '0',
                TeachScheduleEvent.del_flag == '0',
                TeachScheduleEvent.status != '3',
            )
        )
        return result.all()
