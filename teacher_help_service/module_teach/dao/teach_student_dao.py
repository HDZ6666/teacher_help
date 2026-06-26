from datetime import datetime, date
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.vo.teach_student_vo import TeachStudentPageQueryModel
from utils.page_util import PageUtil


class TeachStudentDao:
    """
    学生管理模块数据库操作层
    """

    @classmethod
    async def get_teach_student_list(cls, db: AsyncSession, query_object: TeachStudentPageQueryModel, data_scope_sql: str, is_page: bool = False):
        """
        获取学生分页列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 学生列表信息对象
        """
        query = select(TeachStudent, TeachParent, TeachBaseUser).join(
            TeachParent,
            TeachStudent.parent_id == TeachParent.id
        ).join(
            TeachBaseUser,
            TeachParent.user_id == TeachBaseUser.id
        ).where(
            and_(
                TeachStudent.del_flag == '0',
                TeachParent.del_flag == '0',
                TeachBaseUser.del_flag == '0'
            )
        )
        if query_object.student_name:
            query = query.where(TeachStudent.student_name.like(f'%{query_object.student_name}%'))
        if query_object.parent_name:
            query = query.where(TeachParent.parent_name.like(f'%{query_object.parent_name}%'))
        if query_object.school_name:
            query = query.where(TeachStudent.school_name.like(f'%{query_object.school_name}%'))
        if query_object.grade:
            query = query.where(TeachStudent.grade == query_object.grade)
        if query_object.gender is not None:
            query = query.where(TeachStudent.gender == query_object.gender)
        if query_object.status is not None:
            query = query.where(TeachStudent.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachStudent.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachStudent.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachStudent.create_time))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_student_by_id(cls, db: AsyncSession, student_id: int):
        """
        根据学生ID获取学生详情

        :param db: orm对象
        :param student_id: 学生ID
        :return: 学生详情信息对象
        """
        query = select(TeachStudent, TeachParent, TeachBaseUser).join(
            TeachParent,
            TeachStudent.parent_id == TeachParent.id
        ).join(
            TeachBaseUser,
            TeachParent.user_id == TeachBaseUser.id
        ).where(
            and_(
                TeachStudent.id == student_id,
                TeachStudent.del_flag == '0',
                TeachParent.del_flag == '0',
                TeachBaseUser.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def get_teach_students_by_parent_id(cls, db: AsyncSession, parent_id: int):
        """
        根据家长ID获取学生列表

        :param db: orm对象
        :param parent_id: 家长ID
        :return: 学生列表信息对象
        """
        query = select(TeachStudent).where(
            and_(
                TeachStudent.parent_id == parent_id,
                TeachStudent.del_flag == '0'
            )
        ).order_by(TeachStudent.create_time)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def add_teach_student(cls, db: AsyncSession, student_obj: TeachStudent):
        """
        新增学生

        :param db: orm对象
        :param student_obj: 学生对象
        :return: 新增的学生对象
        """
        db.add(student_obj)
        await db.flush()
        await db.refresh(student_obj)
        return student_obj

    @classmethod
    async def edit_teach_student(cls, db: AsyncSession, student_obj: TeachStudent):
        """
        编辑学生

        :param db: orm对象
        :param student_obj: 学生对象
        :return: 影响的行数
        """
        student_obj.update_time = datetime.now()
        await db.flush()
        return 1

    @classmethod
    async def delete_teach_student(cls, db: AsyncSession, student_ids: List[int]):
        """
        删除学生数据库操作

        :param db: orm对象
        :param student_ids: 学生ID列表
        :return: 删除的行数
        """
        query = select(TeachStudent).where(
            and_(
                TeachStudent.id.in_(student_ids),
                TeachStudent.del_flag == '0'
            )
        )
        result = await db.execute(query)
        students = result.scalars().all()
        count = 0
        for student in students:
            student.del_flag = '2'
            student.update_time = datetime.now()
            count += 1
        await db.flush()
        return count

    @classmethod
    async def get_teach_student_count(cls, db: AsyncSession):
        """
        获取学生总数

        :param db: orm对象
        :return: 学生总数
        """
        query = select(func.count(TeachStudent.id)).where(
            TeachStudent.del_flag == '0'
        )
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def check_student_name_unique(cls, db: AsyncSession, student_name: str, parent_id: int, student_id: int = None):
        """
        检查学生姓名在同一家长下是否唯一

        :param db: orm对象
        :param student_name: 学生姓名
        :param parent_id: 家长ID
        :param student_id: 学生ID
        :return: 校验结果
        """
        query = select(TeachStudent.id).where(
            TeachStudent.student_name == student_name,
            TeachStudent.parent_id == parent_id,
            TeachStudent.del_flag == '0'
        )

        # 编辑时排除自己
        if student_id:
            query = query.where(TeachStudent.id != student_id)

        result = await db.execute(query)
        existing_student = result.scalar()

        return existing_student is None
