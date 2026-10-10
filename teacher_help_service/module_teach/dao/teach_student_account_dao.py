from datetime import datetime
from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.do.teach_class_do import (
    TeachClass,
    TeachClassAttendance,
    TeachClassAttendanceDetail,
    TeachClassStudent,
)
from module_teach.entity.do.teach_comment_do import TeachStudentComment
from module_teach.entity.do.teach_enrollment_order_do import (
    TeachCourseAccountLog,
    TeachEnrollmentOrder,
    TeachEnrollmentOrderItem,
    TeachStudentCourseAccount,
)
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.vo.teach_student_account_vo import TeachCourseAccountPageQueryModel


class TeachStudentAccountDao:
    """
    学员课程账户（报读情况）数据库操作层
    """

    @classmethod
    async def paginate(cls, db: AsyncSession, query, page_num: int, page_size: int):
        total = (await db.execute(select(func.count()).select_from(query.order_by(None).subquery()))).scalar() or 0
        result = await db.execute(query.offset((page_num - 1) * page_size).limit(page_size))
        return result.all(), total

    @classmethod
    async def get_account_list(cls, db: AsyncSession, query_object: TeachCourseAccountPageQueryModel):
        query = (
            select(TeachStudentCourseAccount, TeachStudent, TeachBaseUser.phone, TeachEnrollmentOrder.order_no)
            .join(TeachStudent, TeachStudent.id == TeachStudentCourseAccount.student_id)
            .outerjoin(TeachParent, TeachParent.id == TeachStudent.parent_id)
            .outerjoin(TeachBaseUser, TeachBaseUser.id == TeachParent.user_id)
            .outerjoin(TeachEnrollmentOrder, TeachEnrollmentOrder.id == TeachStudentCourseAccount.order_id)
            .where(TeachStudentCourseAccount.del_flag == 0, TeachStudent.del_flag == '0')
        )
        if query_object.student_id:
            query = query.where(TeachStudentCourseAccount.student_id == query_object.student_id)
        if query_object.student_name:
            keyword = f'%{query_object.student_name.strip()}%'
            query = query.where(or_(TeachStudent.student_name.like(keyword), TeachBaseUser.phone.like(keyword)))
        if query_object.course_id:
            query = query.where(TeachStudentCourseAccount.course_id == query_object.course_id)
        if query_object.course_name:
            query = query.where(TeachStudentCourseAccount.course_name.like(f'%{query_object.course_name.strip()}%'))
        if query_object.class_id:
            query = query.where(TeachStudentCourseAccount.class_id == query_object.class_id)
        if query_object.status:
            query = query.where(TeachStudentCourseAccount.status == query_object.status)
        query = query.order_by(desc(TeachStudentCourseAccount.create_time), desc(TeachStudentCourseAccount.id))
        return await cls.paginate(db, query, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_accounts_for_update(cls, db: AsyncSession, account_ids: list[int]):
        """
        按ID升序加行锁读取课程账户（与点名扣课使用同一把行锁，固定顺序避免死锁）
        """
        await db.flush()
        result = await db.execute(
            select(TeachStudentCourseAccount)
            .where(TeachStudentCourseAccount.id.in_(account_ids), TeachStudentCourseAccount.del_flag == 0)
            .order_by(TeachStudentCourseAccount.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalars().all()

    @classmethod
    async def add_log(cls, db: AsyncSession, log: TeachCourseAccountLog):
        db.add(log)
        await db.flush()
        return log

    @classmethod
    async def get_logs(cls, db: AsyncSession, student_id: int | None = None, account_id: int | None = None):
        query = select(TeachCourseAccountLog)
        if student_id:
            query = query.where(TeachCourseAccountLog.student_id == student_id)
        if account_id:
            query = query.where(TeachCourseAccountLog.account_id == account_id)
        query = query.order_by(desc(TeachCourseAccountLog.create_time), desc(TeachCourseAccountLog.id)).limit(500)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def remove_account_from_classes(cls, db: AsyncSession, account_id: int, update_by: str):
        """
        把绑定该课程账户的在读班级学员标记为已移出，返回受影响的班级ID
        """
        result = await db.execute(
            select(TeachClassStudent.class_id).where(
                TeachClassStudent.course_account_id == account_id,
                TeachClassStudent.status == 1,
                TeachClassStudent.del_flag == 0,
            )
        )
        class_ids = sorted({row[0] for row in result.all()})
        if class_ids:
            await db.execute(
                update(TeachClassStudent)
                .where(
                    TeachClassStudent.course_account_id == account_id,
                    TeachClassStudent.status == 1,
                    TeachClassStudent.del_flag == 0,
                )
                .values(status=2, leave_date=datetime.now().date(), update_by=update_by, update_time=datetime.now())
            )
        return class_ids

    @classmethod
    async def set_class_enroll_status(cls, db: AsyncSession, class_id: int, enroll_status: int):
        await db.execute(
            update(TeachClass)
            .where(TeachClass.id == class_id)
            .values(enroll_status=enroll_status, update_time=datetime.now())
            .execution_options(synchronize_session='fetch')
        )

    @classmethod
    async def get_order_with_items(cls, db: AsyncSession, order_id: int):
        order = (
            (
                await db.execute(
                    select(TeachEnrollmentOrder).where(
                        TeachEnrollmentOrder.id == order_id, TeachEnrollmentOrder.del_flag == 0
                    )
                )
            )
            .scalars()
            .first()
        )
        if not order:
            return None, []
        items = (
            (
                await db.execute(
                    select(TeachEnrollmentOrderItem)
                    .where(TeachEnrollmentOrderItem.order_id == order_id, TeachEnrollmentOrderItem.del_flag == 0)
                    .order_by(TeachEnrollmentOrderItem.sort, TeachEnrollmentOrderItem.id)
                )
            )
            .scalars()
            .all()
        )
        return order, items

    @classmethod
    async def get_student_lessons(cls, db: AsyncSession, student_id: int, page_num: int, page_size: int):
        query = (
            select(TeachClassAttendanceDetail, TeachClassAttendance)
            .join(TeachClassAttendance, TeachClassAttendance.id == TeachClassAttendanceDetail.attendance_id)
            .where(
                TeachClassAttendanceDetail.student_id == student_id,
                TeachClassAttendanceDetail.del_flag == 0,
                TeachClassAttendance.del_flag == 0,
            )
            .order_by(desc(TeachClassAttendance.class_date), desc(TeachClassAttendance.id))
        )
        return await cls.paginate(db, query, page_num, page_size)

    @classmethod
    async def get_student_checkins(cls, db: AsyncSession, student_id: int, page_num: int, page_size: int):
        query = (
            select(TeachScheduleAttendance, TeachScheduleEvent)
            .join(TeachScheduleEvent, TeachScheduleEvent.id == TeachScheduleAttendance.event_id)
            .where(
                TeachScheduleAttendance.student_id == student_id,
                TeachScheduleAttendance.del_flag == '0',
                TeachScheduleEvent.del_flag == '0',
            )
            .order_by(desc(TeachScheduleEvent.start_time), desc(TeachScheduleAttendance.id))
        )
        return await cls.paginate(db, query, page_num, page_size)

    @classmethod
    async def get_student_comments(cls, db: AsyncSession, student_id: int, page_num: int, page_size: int):
        query = (
            select(TeachStudentComment)
            .where(
                TeachStudentComment.student_id == student_id,
                TeachStudentComment.del_flag == 0,
                TeachStudentComment.status == 1,
            )
            .order_by(desc(TeachStudentComment.class_date), desc(TeachStudentComment.id))
        )
        rows, total = await cls.paginate(db, query, page_num, page_size)
        return [row[0] for row in rows], total
