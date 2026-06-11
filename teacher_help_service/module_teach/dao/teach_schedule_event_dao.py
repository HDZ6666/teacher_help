from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
        data_scope_sql: str,
        is_page: bool = False
    ):
        """
        获取排课事件分页列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 排课事件列表信息对象
        """
        query = select(TeachScheduleEvent, TeachTeacher).join(
            TeachTeacher,
            TeachScheduleEvent.teacher_id == TeachTeacher.id
        ).where(
            and_(
                TeachScheduleEvent.del_flag == '0',
                TeachTeacher.del_flag == '0'
            )
        )
        if query_object.teacher_id:
            query = query.where(TeachScheduleEvent.teacher_id == query_object.teacher_id)
        if query_object.subject_code:
            query = query.where(TeachScheduleEvent.subject_code == query_object.subject_code)
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
        query = query.order_by(desc(TeachScheduleEvent.start_time))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_schedule_event_by_id(cls, db: AsyncSession, event_id: int):
        """
        根据ID获取排课事件

        :param db: orm对象
        :param event_id: 事件ID
        :return: 排课事件详情信息对象
        """
        query = select(TeachScheduleEvent, TeachTeacher).join(
            TeachTeacher,
            TeachScheduleEvent.teacher_id == TeachTeacher.id
        ).where(
            and_(
                TeachScheduleEvent.id == event_id,
                TeachScheduleEvent.del_flag == '0',
                TeachTeacher.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def add_teach_schedule_event(cls, db: AsyncSession, event: TeachScheduleEvent):
        """
        新增排课事件

        :param db: orm对象
        :param event: 排课事件对象
        :return: 新增的事件ID
        """
        db.add(event)
        await db.flush()
        return event.id

    @classmethod
    async def edit_teach_schedule_event(cls, db: AsyncSession, event: TeachScheduleEvent):
        """
        编辑排课事件

        :param db: orm对象
        :param event: 排课事件对象
        """
        await db.merge(event)

    @classmethod
    async def delete_teach_schedule_event(cls, db: AsyncSession, event_ids: List[int]):
        """
        删除排课事件数据库操作

        :param db: orm对象
        :param event_ids: 事件ID列表
        """
        query = select(TeachScheduleEvent).where(TeachScheduleEvent.id.in_(event_ids))
        result = await db.execute(query)
        events = result.scalars().all()
        for event in events:
            event.del_flag = '2'
            event.update_time = datetime.now()

    @classmethod
    async def check_time_conflict(
        cls,
        db: AsyncSession,
        teacher_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: Optional[int] = None
    ):
        """
        检查教师时间冲突

        :param db: orm对象
        :param teacher_id: 教师ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param exclude_event_id: 排除的事件ID
        :return: 是否存在冲突
        """
        query = select(func.count(TeachScheduleEvent.id)).where(
            and_(
                TeachScheduleEvent.teacher_id == teacher_id,
                TeachScheduleEvent.del_flag == '0',
                TeachScheduleEvent.status.in_(['0', '1']),  # 已安排或进行中
                TeachScheduleEvent.start_time < end_time,
                TeachScheduleEvent.end_time > start_time
            )
        )

        if exclude_event_id:
            query = query.where(TeachScheduleEvent.id != exclude_event_id)

        result = await db.execute(query)
        count = result.scalar()
        return count > 0

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
        rate: float
    ):
        """
        更新缓存统计数据

        :param db: orm对象
        :param event_id: 事件ID
        :param planned: 计划人数
        :param present: 出勤人数
        :param late: 迟到人数
        :param excused: 请假人数
        :param absent: 缺勤人数
        :param rate: 出勤率
        """
        event = await cls.get_teach_schedule_event_by_id(db, event_id)
        if event:
            event.cached_planned = planned
            event.cached_present = present
            event.cached_late = late
            event.cached_excused = excused
            event.cached_absent = absent
            event.cached_rate = rate
            event.update_time = datetime.now()

