from datetime import datetime
from sqlalchemy import and_, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.entity.do.teach_card_do import TeachCard, TeachCardCourse, TeachCardGrant, TeachCardLog
from module_teach.entity.vo.teach_card_vo import (
    TeachCardGrantPageQueryModel,
    TeachCardLogPageQueryModel,
    TeachCardPageQueryModel,
)
from utils.page_util import PageUtil


class TeachCardDao:
    """
    会员卡模块数据库操作层
    """

    # ------------------------ 卡模板 ------------------------
    @classmethod
    async def get_teach_card_list(
        cls, db: AsyncSession, query_object: TeachCardPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachCard).where(TeachCard.del_flag == 0)
        if query_object.card_name:
            query = query.where(TeachCard.card_name.like(f'%{query_object.card_name}%'))
        if query_object.card_type:
            query = query.where(TeachCard.card_type == query_object.card_type)
        if query_object.status is not None:
            query = query.where(TeachCard.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachCard.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachCard.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachCard.create_time), desc(TeachCard.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_card_by_id(cls, db: AsyncSession, card_id: int):
        result = await db.execute(select(TeachCard).where(TeachCard.id == card_id, TeachCard.del_flag == 0))
        return result.scalars().first()

    @classmethod
    async def get_teach_card_by_no(cls, db: AsyncSession, card_no: str):
        result = await db.execute(select(TeachCard).where(TeachCard.card_no == card_no, TeachCard.del_flag == 0))
        return result.scalars().first()

    @classmethod
    async def add_teach_card(cls, db: AsyncSession, card: TeachCard):
        db.add(card)
        await db.flush()
        await db.refresh(card)
        return card

    @classmethod
    async def edit_teach_card(cls, db: AsyncSession, card: TeachCard):
        card.update_time = datetime.now()
        await db.flush()
        return card

    @classmethod
    async def delete_teach_card(cls, db: AsyncSession, card_ids: list[int], update_by: str):
        await db.execute(
            update(TeachCard)
            .where(and_(TeachCard.id.in_(card_ids), TeachCard.del_flag == 0))
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def update_teach_card_status(cls, db: AsyncSession, card_id: int, status: int, update_by: str):
        await db.execute(
            update(TeachCard)
            .where(and_(TeachCard.id == card_id, TeachCard.del_flag == 0))
            .values(status=status, update_by=update_by, update_time=datetime.now())
        )

    # ------------------------ 适用课程 ------------------------
    @classmethod
    async def get_courses_by_card_id(cls, db: AsyncSession, card_id: int):
        result = await db.execute(
            select(TeachCardCourse)
            .where(TeachCardCourse.card_id == card_id, TeachCardCourse.del_flag == 0)
            .order_by(TeachCardCourse.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_courses_by_card_ids(cls, db: AsyncSession, card_ids: list[int]):
        if not card_ids:
            return []
        result = await db.execute(
            select(TeachCardCourse)
            .where(TeachCardCourse.card_id.in_(card_ids), TeachCardCourse.del_flag == 0)
            .order_by(TeachCardCourse.card_id, TeachCardCourse.id)
        )
        return result.scalars().all()

    @classmethod
    async def delete_courses_by_card_id(cls, db: AsyncSession, card_id: int, update_by: str):
        await db.execute(
            update(TeachCardCourse)
            .where(TeachCardCourse.card_id == card_id, TeachCardCourse.del_flag == 0)
            .values(del_flag=1)
        )

    @classmethod
    async def add_card_course(cls, db: AsyncSession, card_course: TeachCardCourse):
        db.add(card_course)
        await db.flush()
        await db.refresh(card_course)
        return card_course

    # ------------------------ 发放记录 ------------------------
    @classmethod
    async def get_teach_card_grant_list(
        cls, db: AsyncSession, query_object: TeachCardGrantPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachCardGrant).where(TeachCardGrant.del_flag == 0)
        if query_object.card_id:
            query = query.where(TeachCardGrant.card_id == query_object.card_id)
        if query_object.card_name:
            query = query.where(TeachCardGrant.card_name.like(f'%{query_object.card_name}%'))
        if query_object.student_id:
            query = query.where(TeachCardGrant.student_id == query_object.student_id)
        if query_object.student_name:
            query = query.where(TeachCardGrant.student_name.like(f'%{query_object.student_name}%'))
        if query_object.grant_status is not None:
            query = query.where(TeachCardGrant.grant_status == query_object.grant_status)
        if query_object.begin_time:
            query = query.where(TeachCardGrant.grant_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachCardGrant.grant_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachCardGrant.grant_time), desc(TeachCardGrant.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_card_grant_by_id(cls, db: AsyncSession, grant_id: int):
        result = await db.execute(
            select(TeachCardGrant).where(TeachCardGrant.id == grant_id, TeachCardGrant.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def get_grants_by_student_id(cls, db: AsyncSession, student_id: int):
        result = await db.execute(
            select(TeachCardGrant)
            .where(TeachCardGrant.student_id == student_id, TeachCardGrant.del_flag == 0)
            .order_by(desc(TeachCardGrant.grant_time), desc(TeachCardGrant.id))
        )
        return result.scalars().all()

    @classmethod
    async def add_teach_card_grant(cls, db: AsyncSession, grant: TeachCardGrant):
        db.add(grant)
        await db.flush()
        await db.refresh(grant)
        return grant

    @classmethod
    async def edit_teach_card_grant(cls, db: AsyncSession, grant: TeachCardGrant):
        grant.update_time = datetime.now()
        await db.flush()
        return grant

    # ------------------------ 操作记录 ------------------------
    @classmethod
    async def get_teach_card_log_list(
        cls, db: AsyncSession, query_object: TeachCardLogPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachCardLog).where(TeachCardLog.del_flag == 0)
        if query_object.card_id:
            query = query.where(TeachCardLog.card_id == query_object.card_id)
        if query_object.grant_id:
            query = query.where(TeachCardLog.grant_id == query_object.grant_id)
        if query_object.student_id:
            query = query.where(TeachCardLog.student_id == query_object.student_id)
        if query_object.action:
            query = query.where(TeachCardLog.action == query_object.action)
        if query_object.begin_time:
            query = query.where(TeachCardLog.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachCardLog.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachCardLog.create_time), desc(TeachCardLog.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def add_teach_card_log(cls, db: AsyncSession, log: TeachCardLog):
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return log
