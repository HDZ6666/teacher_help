from datetime import datetime
from typing import List

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_teach.entity.do.teach_class_do import TeachClassAttendance, TeachClassAttendanceDetail
from module_teach.entity.do.teach_comment_do import TeachStudentComment
from module_teach.entity.vo.teach_comment_vo import TeachCommentPageQueryModel


class TeachCommentDao:
    """
    课后点评模块数据库操作层
    """

    @classmethod
    async def paginate(cls, db: AsyncSession, query, page_num: int, page_size: int):
        total = (await db.execute(select(func.count()).select_from(query.order_by(None).subquery()))).scalar() or 0
        result = await db.execute(query.offset((page_num - 1) * page_size).limit(page_size))
        return result.all(), total

    @classmethod
    async def get_comment_list(cls, db: AsyncSession, query_object: TeachCommentPageQueryModel):
        """
        获取课后点评分页列表
        """
        query = select(TeachStudentComment).where(TeachStudentComment.del_flag == 0)
        if query_object.class_id:
            query = query.where(TeachStudentComment.class_id == query_object.class_id)
        if query_object.student_id:
            query = query.where(TeachStudentComment.student_id == query_object.student_id)
        if query_object.student_name:
            query = query.where(TeachStudentComment.student_name.like(f'%{query_object.student_name}%'))
        if query_object.course_id:
            query = query.where(TeachStudentComment.course_id == query_object.course_id)
        if query_object.teacher_id:
            query = query.where(TeachStudentComment.teacher_id == query_object.teacher_id)
        if query_object.comment_type:
            query = query.where(TeachStudentComment.comment_type == query_object.comment_type)
        if query_object.status is not None:
            query = query.where(TeachStudentComment.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachStudentComment.class_date >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachStudentComment.class_date <= query_object.end_time)
        query = query.order_by(desc(TeachStudentComment.class_date), desc(TeachStudentComment.id))
        rows, total = await cls.paginate(db, query, query_object.page_num, query_object.page_size)
        return [row[0] for row in rows], total

    @classmethod
    async def get_comment_by_id(cls, db: AsyncSession, comment_id: int):
        """
        根据ID获取点评详情
        """
        result = await db.execute(
            select(TeachStudentComment).where(
                TeachStudentComment.id == comment_id,
                TeachStudentComment.del_flag == 0,
            )
        )
        return result.scalars().first()

    @classmethod
    async def get_attendance_by_id(cls, db: AsyncSession, attendance_id: int):
        """
        根据ID获取点名记录
        """
        result = await db.execute(
            select(TeachClassAttendance).where(
                TeachClassAttendance.id == attendance_id,
                TeachClassAttendance.del_flag == 0,
            )
        )
        return result.scalars().first()

    @classmethod
    async def get_attendance_details(cls, db: AsyncSession, attendance_id: int):
        """
        获取某次点名下的学员明细
        """
        result = await db.execute(
            select(TeachClassAttendanceDetail)
            .where(
                TeachClassAttendanceDetail.attendance_id == attendance_id,
                TeachClassAttendanceDetail.del_flag == 0,
            )
            .order_by(TeachClassAttendanceDetail.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_commented_student_ids(cls, db: AsyncSession, attendance_id: int):
        """
        获取某次点名下已点评的学员ID集合
        """
        result = await db.execute(
            select(TeachStudentComment.student_id).where(
                TeachStudentComment.attendance_id == attendance_id,
                TeachStudentComment.status == 1,
                TeachStudentComment.del_flag == 0,
            )
        )
        return {row[0] for row in result.all()}

    @classmethod
    async def add_comment(cls, db: AsyncSession, comment_obj: TeachStudentComment):
        """
        新增点评
        """
        db.add(comment_obj)
        await db.flush()
        await db.refresh(comment_obj)
        return comment_obj

    @classmethod
    async def add_comments(cls, db: AsyncSession, comment_objs: List[TeachStudentComment]):
        """
        批量新增点评
        """
        db.add_all(comment_objs)
        await db.flush()
        return len(comment_objs)

    @classmethod
    async def edit_comment(cls, db: AsyncSession, comment_obj: TeachStudentComment):
        """
        编辑点评
        """
        comment_obj.update_time = datetime.now()
        await db.flush()
        return 1

    @classmethod
    async def revoke_comment(cls, db: AsyncSession, comment_ids: List[int], current_user_name: str):
        """
        撤销点评(置 status=2 并软删)
        """
        result = await db.execute(
            select(TeachStudentComment).where(
                TeachStudentComment.id.in_(comment_ids),
                TeachStudentComment.del_flag == 0,
            )
        )
        comments = result.scalars().all()
        count = 0
        for comment in comments:
            comment.status = 2
            comment.del_flag = 1
            comment.update_by = current_user_name
            comment.update_time = datetime.now()
            count += 1
        await db.flush()
        return count
