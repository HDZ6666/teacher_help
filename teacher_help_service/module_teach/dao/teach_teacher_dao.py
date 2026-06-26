from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, desc, asc, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.do.teach_teacher_relation_do import TeachTeacherSubject, TeachTeacherGrade
from module_teach.entity.do.teach_subject_do import TeachSubject
from module_teach.entity.do.teach_grade_do import TeachGrade
from module_teach.entity.vo.teach_teacher_vo import TeachTeacherPageQueryModel, TeacherSubjectModel, TeacherGradeModel
from utils.page_util import PageUtil


class TeachTeacherDao:
    """
    教师管理模块数据库操作层
    """

    @classmethod
    async def get_teach_teacher_list(cls, db: AsyncSession, query_object: TeachTeacherPageQueryModel, data_scope_sql: str, is_page: bool = False):
        """
        获取教师分页列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 教师列表信息对象
        """
        query = select(TeachTeacher, TeachBaseUser).join(
            TeachBaseUser,
            TeachTeacher.user_id == TeachBaseUser.id
        ).where(
            and_(
                TeachTeacher.del_flag == '0',
                TeachBaseUser.del_flag == '0'
            )
        )
        if query_object.teacher_name:
            query = query.where(TeachTeacher.teacher_name.like(f'%{query_object.teacher_name}%'))
        if query_object.phone:
            query = query.where(TeachBaseUser.phone.like(f'%{query_object.phone}%'))
        if query_object.teaching_subjects:
            query = query.where(TeachTeacher.teaching_subjects.like(f'%{query_object.teaching_subjects}%'))
        if query_object.status is not None:
            query = query.where(TeachTeacher.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachTeacher.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachTeacher.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachTeacher.create_time))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_teacher_by_id(cls, db: AsyncSession, teacher_id: int):
        """
        根据教师ID获取教师详情

        :param db: orm对象
        :param teacher_id: 教师ID
        :return: 教师详情信息对象
        """
        query = select(TeachTeacher, TeachBaseUser).join(
            TeachBaseUser,
            TeachTeacher.user_id == TeachBaseUser.id
        ).where(
            and_(
                TeachTeacher.id == teacher_id,
                TeachTeacher.del_flag == '0',
                TeachBaseUser.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def get_teach_teacher_by_user_id(cls, db: AsyncSession, user_id: int):
        """
        根据用户ID获取教师信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 教师信息对象
        """
        query = select(TeachTeacher).where(
            and_(
                TeachTeacher.user_id == user_id,
                TeachTeacher.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def add_teach_teacher(cls, db: AsyncSession, teacher_obj: TeachTeacher):
        """
        新增教师

        :param db: orm对象
        :param teacher_obj: 教师对象
        :return: 新增的教师对象
        """
        db.add(teacher_obj)
        await db.flush()
        await db.refresh(teacher_obj)
        return teacher_obj

    @classmethod
    async def edit_teach_teacher(cls, db: AsyncSession, teacher_obj: TeachTeacher):
        """
        编辑教师

        :param db: orm对象
        :param teacher_obj: 教师对象
        :return: 影响的行数
        """
        teacher_obj.update_time = datetime.now()
        await db.flush()
        return 1

    @classmethod
    async def delete_teach_teacher(cls, db: AsyncSession, teacher_ids: List[int]):
        """
        删除教师数据库操作

        :param db: orm对象
        :param teacher_ids: 教师ID列表
        :return: 删除的行数
        """
        query = select(TeachTeacher).where(
            and_(
                TeachTeacher.id.in_(teacher_ids),
                TeachTeacher.del_flag == '0'
            )
        )
        result = await db.execute(query)
        teachers = result.scalars().all()
        count = 0
        for teacher in teachers:
            teacher.del_flag = '2'
            teacher.update_time = datetime.now()
            count += 1
        await db.flush()
        return count

    @classmethod
    async def get_teach_teacher_count(cls, db: AsyncSession):
        """
        获取教师总数

        :param db: orm对象
        :return: 教师总数
        """
        query = select(func.count(TeachTeacher.id)).where(
            TeachTeacher.del_flag == '0'
        )
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def add_teacher_subject_dao(cls, db: AsyncSession, teacher_subject: TeacherSubjectModel):
        """
        新增教师科目关联信息数据库操作

        :param db: orm对象
        :param teacher_subject: 教师科目关联对象
        :return:
        """
        subject_id = getattr(teacher_subject, 'subject_id', None)
        subject_code = getattr(teacher_subject, 'subject_code', None)
        if subject_id is None and subject_code:
            result = await db.execute(
                select(TeachSubject.subject_id).where(
                    TeachSubject.subject_code == subject_code,
                    TeachSubject.del_flag == '0'
                )
            )
            subject_id = result.scalar()
        if subject_id is None:
            return
        db_teacher_subject = TeachTeacherSubject(teacher_id=teacher_subject.teacher_id, subject_id=subject_id)
        db.add(db_teacher_subject)

    @classmethod
    async def delete_teacher_subject_dao(cls, db: AsyncSession, teacher_id: int):
        """
        删除教师科目关联信息数据库操作
        
        :param db: orm对象
        :param teacher_id: 教师ID
        :return:
        """
        await db.execute(
            delete(TeachTeacherSubject).where(TeachTeacherSubject.teacher_id == teacher_id)
        )

    @classmethod
    async def get_teacher_subjects_dao(cls, db: AsyncSession, teacher_id: int) -> List[str]:
        """
        获取教师的科目代码列表
        
        :param db: orm对象
        :param teacher_id: 教师ID
        :return: 科目代码列表
        """
        query = (
            select(TeachSubject.subject_code)
            .join(TeachTeacherSubject, TeachTeacherSubject.subject_id == TeachSubject.subject_id)
            .where(
                TeachTeacherSubject.teacher_id == teacher_id,
                TeachSubject.del_flag == '0'
            )
            .order_by(TeachSubject.subject_sort, TeachSubject.subject_id)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def add_teacher_grade_dao(cls, db: AsyncSession, teacher_grade: TeacherGradeModel):
        """
        新增教师年级关联信息数据库操作
        
        :param db: orm对象
        :param teacher_grade: 教师年级关联对象
        :return:
        """
        grade_id = getattr(teacher_grade, 'grade_id', None)
        grade_code = getattr(teacher_grade, 'grade_code', None)
        if grade_id is None and grade_code:
            result = await db.execute(
                select(TeachGrade.grade_id).where(
                    TeachGrade.grade_code == grade_code
                )
            )
            grade_id = result.scalar()
        if grade_id is None:
            return
        db_teacher_grade = TeachTeacherGrade(teacher_id=teacher_grade.teacher_id, grade_id=grade_id)
        db.add(db_teacher_grade)

    @classmethod
    async def delete_teacher_grade_dao(cls, db: AsyncSession, teacher_id: int):
        """
        删除教师年级关联信息数据库操作
        
        :param db: orm对象
        :param teacher_id: 教师ID
        :return:
        """
        await db.execute(
            delete(TeachTeacherGrade).where(TeachTeacherGrade.teacher_id == teacher_id)
        )

    @classmethod
    async def get_teacher_grades_dao(cls, db: AsyncSession, teacher_id: int) -> List[str]:
        """
        获取教师的年级代码列表
        
        :param db: orm对象
        :param teacher_id: 教师ID
        :return: 年级代码列表
        """
        query = (
            select(TeachGrade.grade_code)
            .join(TeachTeacherGrade, TeachTeacherGrade.grade_id == TeachGrade.grade_id)
            .where(TeachTeacherGrade.teacher_id == teacher_id)
            .order_by(TeachGrade.grade_sort, TeachGrade.grade_id)
        )
        result = await db.execute(query)
        return result.scalars().all()
