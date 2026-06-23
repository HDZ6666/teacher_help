from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from module_teach.entity.vo.teach_schedule_event_vo import TeachScheduleEventPageQueryModel
from utils.page_util import PageUtil


class TeachScheduleEventDao:
    """
    排课事件管理模块数据库操作层
    """

    @classmethod
    async def get_teach_schedule_event_list(
        cls,
        db: AsyncSession,
        query_object: TeachScheduleEventPageQueryModel,
        data_scope_sql: str = '',
        is_page: bool = False,
    ):
        """
        获取排课事件分页列表
        """
        query = (
            select(TeachScheduleEvent, TeachTeacher, TeachCourse)
            .outerjoin(
                TeachTeacher,
                and_(TeachScheduleEvent.teacher_id == TeachTeacher.id, TeachTeacher.del_flag == '0'),
            )
            .outerjoin(
                TeachCourse,
                and_(TeachScheduleEvent.course_id == TeachCourse.id, TeachCourse.del_flag == 0),
            )
            .where(TeachScheduleEvent.del_flag == '0')
        )
        if query_object.teacher_id:
            query = query.where(TeachScheduleEvent.teacher_id == query_object.teacher_id)
        if query_object.class_id:
            query = query.where(TeachScheduleEvent.class_id == query_object.class_id)
        if query_object.course_id:
            query = query.where(TeachScheduleEvent.course_id == query_object.course_id)
        if query_object.subject_code:
            query = query.where(TeachScheduleEvent.subject_code == query_object.subject_code)
        if query_object.classroom:
            query = query.where(TeachScheduleEvent.classroom == query_object.classroom)
        if query_object.status is not None:
            query = query.where(TeachScheduleEvent.status == query_object.status)
        if query_object.event_date:
            query = query.where(TeachScheduleEvent.event_date == query_object.event_date)
        if query_object.start_time:
            query = query.where(TeachScheduleEvent.start_time >= query_object.start_time)
        if query_object.end_time:
            query = query.where(TeachScheduleEvent.end_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(TeachScheduleEvent.event_date, TeachScheduleEvent.start_time, desc(TeachScheduleEvent.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_schedule_event_by_id(cls, db: AsyncSession, event_id: int):
        """
        根据ID获取排课事件详情
        """
        query = (
            select(TeachScheduleEvent, TeachTeacher, TeachCourse)
            .outerjoin(
                TeachTeacher,
                and_(TeachScheduleEvent.teacher_id == TeachTeacher.id, TeachTeacher.del_flag == '0'),
            )
            .outerjoin(
                TeachCourse,
                and_(TeachScheduleEvent.course_id == TeachCourse.id, TeachCourse.del_flag == 0),
            )
            .where(TeachScheduleEvent.id == event_id, TeachScheduleEvent.del_flag == '0')
        )
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def get_raw_schedule_event_by_id(cls, db: AsyncSession, event_id: int):
        result = await db.execute(
            select(TeachScheduleEvent).where(TeachScheduleEvent.id == event_id, TeachScheduleEvent.del_flag == '0')
        )
        return result.scalars().first()

    @classmethod
    async def get_raw_schedule_events_by_ids(cls, db: AsyncSession, event_ids: List[int]):
        result = await db.execute(
            select(TeachScheduleEvent).where(TeachScheduleEvent.id.in_(event_ids), TeachScheduleEvent.del_flag == '0')
        )
        return result.scalars().all()

    @classmethod
    async def add_teach_schedule_event(cls, db: AsyncSession, event: TeachScheduleEvent):
        """
        新增排课事件
        """
        db.add(event)
        await db.flush()
        await db.refresh(event)
        return event.id

    @classmethod
    async def edit_teach_schedule_event(cls, db: AsyncSession, event: TeachScheduleEvent):
        """
        编辑排课事件
        """
        event.update_time = datetime.now()
        await db.flush()
        return event

    @classmethod
    async def delete_teach_schedule_event(cls, db: AsyncSession, event_ids: List[int], update_by: str | None = None):
        """
        删除排课事件数据库操作
        """
        events = await cls.get_raw_schedule_events_by_ids(db, event_ids)
        for event in events:
            event.del_flag = '2'
            event.update_by = update_by or event.update_by
            event.update_time = datetime.now()

    @classmethod
    async def count_class_events(cls, db: AsyncSession, class_id: int):
        result = await db.execute(
            select(func.count(TeachScheduleEvent.id)).where(
                TeachScheduleEvent.class_id == class_id,
                TeachScheduleEvent.del_flag == '0',
                TeachScheduleEvent.status != '3',
            )
        )
        return result.scalar() or 0

    @classmethod
    async def has_resource_conflict(
        cls,
        db: AsyncSession,
        start_time: datetime,
        end_time: datetime,
        teacher_id: Optional[int] = None,
        class_id: Optional[int] = None,
        classroom: Optional[str] = None,
        exclude_event_id: Optional[int] = None,
    ):
        """
        检查老师、班级、教室是否有时间重叠。
        """
        resource_conditions = []
        if teacher_id:
            resource_conditions.append(TeachScheduleEvent.teacher_id == teacher_id)
        if class_id:
            resource_conditions.append(TeachScheduleEvent.class_id == class_id)
        if classroom:
            resource_conditions.append(TeachScheduleEvent.classroom == classroom)
        if not resource_conditions:
            return []

        query = select(TeachScheduleEvent).where(
            TeachScheduleEvent.del_flag == '0',
            TeachScheduleEvent.status.in_(['0', '1']),
            TeachScheduleEvent.start_time < end_time,
            TeachScheduleEvent.end_time > start_time,
            or_(*resource_conditions),
        )
        if exclude_event_id:
            query = query.where(TeachScheduleEvent.id != exclude_event_id)

        result = await db.execute(query)
        events = result.scalars().all()
        conflicts = []
        for event in events:
            if teacher_id and event.teacher_id == teacher_id:
                conflicts.append('上课老师')
            if class_id and event.class_id == class_id:
                conflicts.append('上课班级')
            if classroom and event.classroom == classroom:
                conflicts.append('上课教室')
        return sorted(set(conflicts))

    @classmethod
    async def check_time_conflict(
        cls,
        db: AsyncSession,
        teacher_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: Optional[int] = None,
    ):
        """
        兼容旧调用：检查教师时间冲突。
        """
        conflicts = await cls.has_resource_conflict(
            db,
            start_time,
            end_time,
            teacher_id=teacher_id,
            exclude_event_id=exclude_event_id,
        )
        return bool(conflicts)

    @classmethod
    async def update_cached_stats(
        cls,
        db: AsyncSession,
        event_id: int,
        planned: int,
        present: int,
        late: int,
        excused: int,
        absent: int,
        rate: float,
    ):
        """
        更新缓存统计数据
        """
        event = await cls.get_raw_schedule_event_by_id(db, event_id)
        if event:
            event.cached_planned = planned
            event.cached_present = present
            event.cached_late = late
            event.cached_excused = excused
            event.cached_absent = absent
            event.cached_rate = rate
            event.update_time = datetime.now()
