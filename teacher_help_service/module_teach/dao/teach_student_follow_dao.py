from datetime import datetime, time
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.entity.do.teach_student_follow_do import TeachStudentFollow
from module_teach.entity.vo.teach_student_account_vo import TeachStudentFollowPageQueryModel


class TeachStudentFollowDao:
    """
    学员跟进记录数据库操作层
    """

    @classmethod
    async def get_follow_list(cls, db: AsyncSession, query_object: TeachStudentFollowPageQueryModel):
        query = select(TeachStudentFollow).where(TeachStudentFollow.del_flag == 0)
        if query_object.student_id:
            query = query.where(TeachStudentFollow.student_id == query_object.student_id)
        if query_object.student_name:
            query = query.where(TeachStudentFollow.student_name.like(f'%{query_object.student_name.strip()}%'))
        if query_object.follow_type:
            query = query.where(TeachStudentFollow.follow_type == query_object.follow_type)
        if query_object.begin_time:
            query = query.where(TeachStudentFollow.follow_time >= datetime.combine(query_object.begin_time, time.min))
        if query_object.end_time:
            query = query.where(TeachStudentFollow.follow_time <= datetime.combine(query_object.end_time, time.max))
        query = query.order_by(desc(TeachStudentFollow.follow_time), desc(TeachStudentFollow.id))
        total = (await db.execute(select(func.count()).select_from(query.order_by(None).subquery()))).scalar() or 0
        page_num, page_size = query_object.page_num, query_object.page_size
        result = await db.execute(query.offset((page_num - 1) * page_size).limit(page_size))
        return result.scalars().all(), total

    @classmethod
    async def get_follow_by_id(cls, db: AsyncSession, follow_id: int):
        result = await db.execute(
            select(TeachStudentFollow).where(TeachStudentFollow.id == follow_id, TeachStudentFollow.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def add_follow(cls, db: AsyncSession, follow: TeachStudentFollow):
        db.add(follow)
        await db.flush()
        return follow

    @classmethod
    async def delete_follows(cls, db: AsyncSession, follow_ids: list[int], update_by: str):
        result = await db.execute(
            update(TeachStudentFollow)
            .where(TeachStudentFollow.id.in_(follow_ids), TeachStudentFollow.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )
        return result.rowcount
