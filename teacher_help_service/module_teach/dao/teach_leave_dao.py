from datetime import datetime

from sqlalchemy import and_, desc, false, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_teach.entity.do.teach_class_do import TeachClassAttendanceDetail
from module_teach.entity.do.teach_leave_do import TeachLeaveApplication
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.vo.teach_leave_vo import TeachLeavePageQueryModel


class TeachLeaveDao:
    """
    请假申请模块数据库操作层
    """

    @classmethod
    async def paginate(cls, db: AsyncSession, query, page_num: int, page_size: int):
        total = (await db.execute(select(func.count()).select_from(query.order_by(None).subquery()))).scalar() or 0
        result = await db.execute(query.offset((page_num - 1) * page_size).limit(page_size))
        return result.scalars().all(), total

    @classmethod
    async def get_leave_list(cls, db: AsyncSession, query_object: TeachLeavePageQueryModel):
        query = select(TeachLeaveApplication).where(TeachLeaveApplication.del_flag == 0)
        if query_object.student_id:
            query = query.where(TeachLeaveApplication.student_id == query_object.student_id)
        if query_object.student_keyword:
            keyword = f'%{query_object.student_keyword}%'
            query = query.where(
                or_(
                    TeachLeaveApplication.student_name.like(keyword),
                    TeachLeaveApplication.leave_no.like(keyword),
                )
            )
        if query_object.class_id:
            query = query.where(TeachLeaveApplication.class_id == query_object.class_id)
        if query_object.course_id:
            query = query.where(TeachLeaveApplication.course_id == query_object.course_id)
        if query_object.leave_type is not None:
            query = query.where(TeachLeaveApplication.leave_type == query_object.leave_type)
        if query_object.leave_status is not None:
            query = query.where(TeachLeaveApplication.leave_status == query_object.leave_status)
        if query_object.begin_time:
            query = query.where(TeachLeaveApplication.leave_date >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachLeaveApplication.leave_date <= query_object.end_time)
        query = query.order_by(desc(TeachLeaveApplication.apply_time), desc(TeachLeaveApplication.id))
        return await cls.paginate(db, query, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_leave_by_id(cls, db: AsyncSession, leave_id: int, for_update: bool = False):
        query = select(TeachLeaveApplication).where(
            TeachLeaveApplication.id == leave_id,
            TeachLeaveApplication.del_flag == 0,
        )
        if for_update:
            # 审批前加锁，防止并发重复审批
            await db.flush()
            query = query.with_for_update().execution_options(populate_existing=True)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_leaves_by_ids(cls, db: AsyncSession, leave_ids: list[int]):
        if not leave_ids:
            return []
        result = await db.execute(
            select(TeachLeaveApplication).where(
                TeachLeaveApplication.id.in_(leave_ids),
                TeachLeaveApplication.del_flag == 0,
            )
        )
        return result.scalars().all()

    @classmethod
    async def get_approved_leaves_for_roll_call(
        cls, db: AsyncSession, class_id: int, student_ids: list[int], event_id: int | None, class_date
    ):
        """
        查询点名时生效的“已通过”请假：
        1. 按课次请假：leave.event_id == 本次课次
        2. 按日期请假：leave.event_id 为空、leave_date == 上课日期，且未指定班级或班级一致
        """
        if not student_ids:
            return []
        by_event = TeachLeaveApplication.event_id == event_id if event_id else false()
        by_date = and_(
            TeachLeaveApplication.event_id.is_(None),
            TeachLeaveApplication.leave_date == class_date,
            or_(TeachLeaveApplication.class_id.is_(None), TeachLeaveApplication.class_id == class_id),
        )
        result = await db.execute(
            select(TeachLeaveApplication)
            .where(
                TeachLeaveApplication.del_flag == 0,
                TeachLeaveApplication.leave_status == 2,
                TeachLeaveApplication.student_id.in_(student_ids),
                or_(by_event, by_date),
            )
            .order_by(TeachLeaveApplication.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_class_events_by_date(cls, db: AsyncSession, class_id: int, event_date):
        """获取班级某日未取消的排课课次"""
        result = await db.execute(
            select(TeachScheduleEvent).where(
                TeachScheduleEvent.class_id == class_id,
                TeachScheduleEvent.event_date == event_date,
                TeachScheduleEvent.del_flag == '0',
                TeachScheduleEvent.status != '3',
            )
        )
        return result.scalars().all()

    @classmethod
    async def get_attendance_detail_for_update(cls, db: AsyncSession, attendance_id: int, student_id: int):
        """加锁读取某次点名中某个学员的明细"""
        await db.flush()
        result = await db.execute(
            select(TeachClassAttendanceDetail)
            .where(
                TeachClassAttendanceDetail.attendance_id == attendance_id,
                TeachClassAttendanceDetail.student_id == student_id,
                TeachClassAttendanceDetail.del_flag == 0,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalars().first()

    @classmethod
    async def add_leave(cls, db: AsyncSession, leave_obj: TeachLeaveApplication):
        db.add(leave_obj)
        await db.flush()
        await db.refresh(leave_obj)
        return leave_obj

    @classmethod
    async def edit_leave(cls, db: AsyncSession, leave_obj: TeachLeaveApplication):
        leave_obj.update_time = datetime.now()
        await db.flush()
        return leave_obj

    @classmethod
    async def delete_leave(cls, db: AsyncSession, leave_ids: list[int], update_by: str):
        await db.execute(
            update(TeachLeaveApplication)
            .where(TeachLeaveApplication.id.in_(leave_ids), TeachLeaveApplication.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )
