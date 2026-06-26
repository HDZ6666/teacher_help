from datetime import datetime

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_teach.entity.do.teach_leave_do import TeachLeaveApplication
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
    async def get_leave_by_id(cls, db: AsyncSession, leave_id: int):
        result = await db.execute(
            select(TeachLeaveApplication).where(
                TeachLeaveApplication.id == leave_id,
                TeachLeaveApplication.del_flag == 0,
            )
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
