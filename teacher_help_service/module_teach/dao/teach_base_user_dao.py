from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.vo.teach_teacher_vo import TeachTeacherPageQueryModel
from module_teach.entity.vo.teach_parent_vo import TeachParentPageQueryModel
from utils.page_util import PageUtil


class TeachBaseUserDao:
    """
    基础用户管理模块数据库操作层
    """

    @classmethod
    async def get_teach_base_user_by_id(cls, db: AsyncSession, user_id: int):
        """
        根据用户ID获取基础用户信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 基础用户信息对象
        """
        query = select(TeachBaseUser).where(
            and_(
                TeachBaseUser.id == user_id,
                TeachBaseUser.del_flag == 0
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_teach_base_user_by_phone(cls, db: AsyncSession, phone: str):
        """
        根据手机号获取基础用户信息

        :param db: orm对象
        :param phone: 手机号
        :return: 基础用户信息对象
        """
        query = select(TeachBaseUser).where(
            and_(
                TeachBaseUser.phone == phone,
                TeachBaseUser.del_flag == 0
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def add_teach_base_user(cls, db: AsyncSession, user_obj: TeachBaseUser):
        """
        新增基础用户

        :param db: orm对象
        :param user_obj: 基础用户对象
        :return: 新增的基础用户对象
        """
        db.add(user_obj)
        await db.flush()
        await db.refresh(user_obj)
        return user_obj

    @classmethod
    async def edit_teach_base_user(cls, db: AsyncSession, user_obj: TeachBaseUser):
        """
        编辑基础用户

        :param db: orm对象
        :param user_obj: 基础用户对象
        :return: 影响的行数
        """
        user_obj.update_time = datetime.now()
        await db.flush()
        return 1

    @classmethod
    async def delete_teach_base_user(cls, db: AsyncSession, user_ids: List[int]):
        """
        删除基础用户数据库操作

        :param db: orm对象
        :param user_ids: 用户ID列表
        :return: 删除的行数
        """
        query = select(TeachBaseUser).where(
            and_(
                TeachBaseUser.id.in_(user_ids),
                TeachBaseUser.del_flag == 0
            )
        )
        result = await db.execute(query)
        users = result.scalars().all()
        count = 0
        for user in users:
            user.del_flag = 1
            user.update_time = datetime.now()
            count += 1
        await db.flush()
        return count

    @classmethod
    async def get_teach_base_user_count(cls, db: AsyncSession, user_type: int = None):
        """
        获取基础用户总数

        :param db: orm对象
        :param user_type: 用户类型
        :return: 用户总数
        """
        query = select(func.count(TeachBaseUser.id)).where(
            TeachBaseUser.del_flag == 0
        )
        if user_type:
            query = query.where(TeachBaseUser.user_type == user_type)
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def check_teach_base_user_phone_unique(cls, db: AsyncSession, phone: str, user_id: int = None):
        """
        检查手机号是否唯一

        :param db: orm对象
        :param phone: 手机号
        :param user_id: 用户ID
        :return: 校验结果
        """
        query = select(TeachBaseUser).where(
            and_(
                TeachBaseUser.phone == phone,
                TeachBaseUser.del_flag == 0
            )
        )
        if user_id:
            query = query.where(TeachBaseUser.id != user_id)
        result = await db.execute(query)
        user = result.scalars().first()
        return user is None

    @classmethod
    async def update_last_login_time(cls, db: AsyncSession, user_id: int):
        """
        更新最后登录时间

        :param db: orm对象
        :param user_id: 用户ID
        :return: 影响的行数
        """
        query = select(TeachBaseUser).where(
            and_(
                TeachBaseUser.id == user_id,
                TeachBaseUser.del_flag == 0
            )
        )
        result = await db.execute(query)
        user = result.scalars().first()
        if user:
            user.last_login_at = datetime.now()
            user.update_time = datetime.now()
            await db.flush()
            return 1
        return 0
