from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_comment_dao import TeachCommentDao
from module_teach.entity.do.teach_comment_do import TeachStudentComment
from module_teach.entity.vo.teach_comment_vo import (
    AddTeachCommentModel,
    BatchTeachCommentModel,
    DeleteTeachCommentModel,
    EditTeachCommentModel,
    TeachCommentPageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachCommentService:
    """
    课后点评模块服务层
    """

    STATUS_LABELS = {
        1: '已发布',
        2: '已撤销',
    }

    ATTENDANCE_STATUS_LABELS = {
        1: '到课',
        2: '迟到',
        3: '请假',
        4: '未到',
    }

    @classmethod
    def make_page(cls, rows: list, total: int, page_num: int, page_size: int):
        return PageResponseModel(
            rows=rows,
            pageNum=page_num,
            pageSize=page_size,
            total=total,
            hasNext=total > page_num * page_size,
        )

    @classmethod
    def format_comment_row(cls, comment: TeachStudentComment):
        row = CamelCaseUtil.transform_result(comment)
        row['statusName'] = cls.STATUS_LABELS.get(comment.status, '-')
        return row

    @classmethod
    async def get_comment_list_services(cls, query_db: AsyncSession, query_object: TeachCommentPageQueryModel):
        """
        获取课后点评列表service
        """
        rows, total = await TeachCommentDao.get_comment_list(query_db, query_object)
        return cls.make_page(
            [cls.format_comment_row(row) for row in rows],
            total,
            query_object.page_num,
            query_object.page_size,
        )

    @classmethod
    async def get_comment_detail_services(cls, query_db: AsyncSession, comment_id: int):
        """
        获取课后点评详情service
        """
        comment = await TeachCommentDao.get_comment_by_id(query_db, comment_id)
        if not comment:
            raise ServiceException(message='点评记录不存在')
        return cls.format_comment_row(comment)

    @classmethod
    async def get_pending_students_services(cls, query_db: AsyncSession, attendance_id: int):
        """
        获取某次点名下未点评学员列表service
        """
        attendance = await TeachCommentDao.get_attendance_by_id(query_db, attendance_id)
        if not attendance:
            raise ServiceException(message='点名记录不存在')
        details = await TeachCommentDao.get_attendance_details(query_db, attendance_id)
        commented_ids = await TeachCommentDao.get_commented_student_ids(query_db, attendance_id)
        pending = []
        for detail in details:
            if detail.student_id in commented_ids:
                continue
            pending.append(
                {
                    'attendanceId': attendance.id,
                    'attendanceDetailId': detail.id,
                    'classId': attendance.class_id,
                    'className': attendance.class_name,
                    'studentId': detail.student_id,
                    'studentName': detail.student_name,
                    'courseId': attendance.course_id,
                    'courseName': attendance.course_name,
                    'teacherId': attendance.teacher_id,
                    'teacherName': attendance.teacher_name,
                    'classDate': attendance.class_date,
                    'attendanceStatus': detail.status,
                    'attendanceStatusName': cls.ATTENDANCE_STATUS_LABELS.get(detail.status, '-'),
                }
            )
        return pending

    @classmethod
    async def add_comment_services(
        cls, query_db: AsyncSession, add_comment: AddTeachCommentModel, current_user_name: str
    ):
        """
        发布点评(单个)service
        """
        try:
            class_date = add_comment.class_date
            class_id = add_comment.class_id
            course_id = add_comment.course_id
            course_name = add_comment.course_name
            teacher_id = add_comment.teacher_id
            teacher_name = add_comment.teacher_name
            student_name = add_comment.student_name
            if add_comment.attendance_id:
                attendance = await TeachCommentDao.get_attendance_by_id(query_db, add_comment.attendance_id)
                if attendance:
                    class_id = class_id or attendance.class_id
                    course_id = course_id or attendance.course_id
                    course_name = course_name or attendance.course_name
                    teacher_id = teacher_id or attendance.teacher_id
                    teacher_name = teacher_name or attendance.teacher_name
                    class_date = class_date or attendance.class_date
            comment = TeachStudentComment(
                attendance_id=add_comment.attendance_id,
                attendance_detail_id=add_comment.attendance_detail_id,
                class_id=class_id,
                student_id=add_comment.student_id,
                student_name=student_name,
                course_id=course_id,
                course_name=course_name,
                teacher_id=teacher_id,
                teacher_name=teacher_name,
                class_date=class_date,
                performance_score=add_comment.performance_score,
                homework_score=add_comment.homework_score,
                comment_content=add_comment.comment_content,
                strengths=add_comment.strengths,
                weaknesses=add_comment.weaknesses,
                suggestions=add_comment.suggestions,
                comment_type=add_comment.comment_type or 'single',
                status=1,
                create_by=current_user_name,
                update_by=current_user_name,
                remark=add_comment.remark,
            )
            await TeachCommentDao.add_comment(query_db, comment)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='点评发布成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def batch_comment_services(
        cls, query_db: AsyncSession, batch_comment: BatchTeachCommentModel, current_user_name: str
    ):
        """
        批量/统一点评(一组学员用同一内容)service
        """
        if not batch_comment.student_ids:
            raise ServiceException(message='请至少选择一名学员')
        try:
            class_id = batch_comment.class_id
            course_id = batch_comment.course_id
            course_name = batch_comment.course_name
            teacher_id = batch_comment.teacher_id
            teacher_name = batch_comment.teacher_name
            class_date = batch_comment.class_date
            detail_map = {}
            if batch_comment.attendance_id:
                attendance = await TeachCommentDao.get_attendance_by_id(query_db, batch_comment.attendance_id)
                if attendance:
                    class_id = class_id or attendance.class_id
                    course_id = course_id or attendance.course_id
                    course_name = course_name or attendance.course_name
                    teacher_id = teacher_id or attendance.teacher_id
                    teacher_name = teacher_name or attendance.teacher_name
                    class_date = class_date or attendance.class_date
                details = await TeachCommentDao.get_attendance_details(query_db, batch_comment.attendance_id)
                detail_map = {detail.student_id: detail for detail in details}
            comment_objs = []
            for student_id in batch_comment.student_ids:
                detail = detail_map.get(student_id)
                comment_objs.append(
                    TeachStudentComment(
                        attendance_id=batch_comment.attendance_id,
                        attendance_detail_id=detail.id if detail else None,
                        class_id=class_id,
                        student_id=student_id,
                        student_name=detail.student_name if detail else None,
                        course_id=course_id,
                        course_name=course_name,
                        teacher_id=teacher_id,
                        teacher_name=teacher_name,
                        class_date=class_date,
                        performance_score=batch_comment.performance_score,
                        homework_score=batch_comment.homework_score,
                        comment_content=batch_comment.comment_content,
                        strengths=batch_comment.strengths,
                        weaknesses=batch_comment.weaknesses,
                        suggestions=batch_comment.suggestions,
                        comment_type=batch_comment.comment_type or 'unified',
                        status=1,
                        create_by=current_user_name,
                        update_by=current_user_name,
                        remark=batch_comment.remark,
                    )
                )
            count = await TeachCommentDao.add_comments(query_db, comment_objs)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message=f'批量点评成功，共{count}条')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_comment_services(
        cls, query_db: AsyncSession, edit_comment: EditTeachCommentModel, current_user_name: str
    ):
        """
        编辑点评service
        """
        comment = await TeachCommentDao.get_comment_by_id(query_db, edit_comment.id)
        if not comment:
            raise ServiceException(message='点评记录不存在')
        try:
            if edit_comment.performance_score is not None:
                comment.performance_score = edit_comment.performance_score
            if edit_comment.homework_score is not None:
                comment.homework_score = edit_comment.homework_score
            if edit_comment.comment_content is not None:
                comment.comment_content = edit_comment.comment_content
            if edit_comment.strengths is not None:
                comment.strengths = edit_comment.strengths
            if edit_comment.weaknesses is not None:
                comment.weaknesses = edit_comment.weaknesses
            if edit_comment.suggestions is not None:
                comment.suggestions = edit_comment.suggestions
            if edit_comment.status is not None:
                comment.status = edit_comment.status
            if edit_comment.remark is not None:
                comment.remark = edit_comment.remark
            comment.update_by = current_user_name
            await TeachCommentDao.edit_comment(query_db, comment)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='点评更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_comment_services(
        cls, query_db: AsyncSession, delete_comment: DeleteTeachCommentModel, current_user_name: str
    ):
        """
        撤销点评service
        """
        comment_ids = [int(id_str) for id_str in delete_comment.ids.split(',') if id_str.strip()]
        if not comment_ids:
            raise ServiceException(message='请选择要撤销的点评')
        try:
            count = await TeachCommentDao.revoke_comment(query_db, comment_ids, current_user_name)
            await query_db.commit()
            if count == 0:
                raise ServiceException(message='撤销失败，点评不存在或已被撤销')
            return CrudResponseModel(is_success=True, message='点评撤销成功')
        except Exception as e:
            await query_db.rollback()
            raise e
