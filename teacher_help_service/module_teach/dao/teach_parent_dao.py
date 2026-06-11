from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.vo.teach_parent_vo import TeachParentPageQueryModel
from utils.page_util import PageUtil


class TeachParentDao:
    """
    家长管理模块数据库操作层
    """

    @classmethod
    async def get_teach_parent_list(cls, db: AsyncSession, query_object: TeachParentPageQueryModel, data_scope_sql: str, is_page: bool = False):
        """
        获取家长分页列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 家长列表信息对象
        """
        query = select(TeachParent, TeachBaseUser).join(
            TeachBaseUser,
            TeachParent.user_id == TeachBaseUser.id
        ).where(
            and_(
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0
            )
        )
        if query_object.parent_name:
            query = query.where(TeachParent.parent_name.like(f'%{query_object.parent_name}%'))
        if query_object.phone:
            query = query.where(TeachBaseUser.phone.like(f'%{query_object.phone}%'))
        if query_object.wechat_id:
            query = query.where(TeachParent.wechat_id.like(f'%{query_object.wechat_id}%'))
        if query_object.status is not None:
            query = query.where(TeachParent.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachParent.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachParent.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachParent.create_time))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_parent_by_id(cls, db: AsyncSession, parent_id: int):
        """
        根据家长ID获取家长详情

        :param db: orm对象
        :param parent_id: 家长ID
        :return: 家长详情信息对象
        """
        query = select(TeachParent, TeachBaseUser).join(
            TeachBaseUser,
            TeachParent.user_id == TeachBaseUser.id
        ).where(
            and_(
                TeachParent.id == parent_id,
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0
            )
        )
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def get_teach_parent_by_user_id(cls, db: AsyncSession, user_id: int):
        """
        根据用户ID获取家长信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 家长信息对象
        """
        query = select(TeachParent).where(
            and_(
                TeachParent.user_id == user_id,
                TeachParent.del_flag == 0
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def add_teach_parent(cls, db: AsyncSession, parent_obj: TeachParent):
        """
        新增家长

        :param db: orm对象
        :param parent_obj: 家长对象
        :return: 新增的家长对象
        """
        db.add(parent_obj)
        await db.flush()
        await db.refresh(parent_obj)
        return parent_obj

    @classmethod
    async def edit_teach_parent(cls, db: AsyncSession, parent_obj: TeachParent):
        """
        编辑家长

        :param db: orm对象
        :param parent_obj: 家长对象
        :return: 影响的行数
        """
        parent_obj.update_time = datetime.now()
        await db.flush()
        return 1

    @classmethod
    async def delete_teach_parent(cls, db: AsyncSession, parent_ids: List[int]):
        """
        删除家长数据库操作

        :param db: orm对象
        :param parent_ids: 家长ID列表
        :return: 删除的行数
        """
        query = select(TeachParent).where(
            and_(
                TeachParent.id.in_(parent_ids),
                TeachParent.del_flag == 0
            )
        )
        result = await db.execute(query)
        parents = result.scalars().all()
        count = 0
        for parent in parents:
            parent.del_flag = 1
            parent.update_time = datetime.now()
            count += 1
        await db.flush()
        return count

    @classmethod
    async def get_teach_parent_count(cls, db: AsyncSession):
        """
        获取家长总数

        :param db: orm对象
        :return: 家长总数
        """
        query = select(func.count(TeachParent.id)).where(
            TeachParent.del_flag == 0
        )
        result = await db.execute(query)
        return result.scalar()
