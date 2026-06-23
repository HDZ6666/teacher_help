from datetime import datetime
from sqlalchemy import and_, desc, exists, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.dept_do import SysDept  # noqa: F401
from module_admin.entity.do.role_do import SysRoleDept  # noqa: F401
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.do.teach_class_do import (
    TeachClass,
    TeachClassAttendance,
    TeachClassAttendanceDetail,
    TeachClassStudent,
    TeachClassTeacher,
)
from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from module_teach.entity.vo.teach_class_vo import TeachClassPageQueryModel
from utils.page_util import PageUtil


class TeachClassDao:
    """
    班级管理模块数据库操作层
    """

    @classmethod
    async def get_teach_class_list(
        cls, db: AsyncSession, query_object: TeachClassPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachClass).where(TeachClass.del_flag == 0)
        if query_object.class_name:
            query = query.where(TeachClass.class_name.like(f'%{query_object.class_name}%'))
        if query_object.class_mode:
            query = query.where(TeachClass.class_mode == query_object.class_mode)
        if query_object.class_type:
            query = query.where(TeachClass.class_type == query_object.class_type)
        if query_object.course_id:
            query = query.where(TeachClass.course_id == query_object.course_id)
        if query_object.teacher_id:
            query = query.where(TeachClass.teacher_id == query_object.teacher_id)
        if query_object.enroll_status is not None:
            query = query.where(TeachClass.enroll_status == query_object.enroll_status)
        if query_object.status is not None:
            query = query.where(TeachClass.status == query_object.status)
        if query_object.student_keyword:
            keyword = f'%{query_object.student_keyword}%'
            query = query.where(
                exists()
                .where(
                    TeachClassStudent.class_id == TeachClass.id,
                    TeachClassStudent.status == 1,
                    TeachClassStudent.del_flag == 0,
                    TeachClassStudent.student_id == TeachStudent.id,
                    TeachStudent.parent_id == TeachParent.id,
                    TeachParent.user_id == TeachBaseUser.id,
                    TeachStudent.del_flag == 0,
                    TeachParent.del_flag == 0,
                    TeachBaseUser.del_flag == 0,
                    or_(TeachStudent.student_name.like(keyword), TeachBaseUser.phone.like(keyword)),
                )
                .correlate(TeachClass)
            )
        if query_object.begin_time:
            query = query.where(TeachClass.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachClass.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachClass.create_time), desc(TeachClass.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_class_by_id(cls, db: AsyncSession, class_id: int):
        result = await db.execute(select(TeachClass).where(TeachClass.id == class_id, TeachClass.del_flag == 0))
        return result.scalars().first()

    @classmethod
    async def get_teach_class_by_no(cls, db: AsyncSession, class_no: str):
        result = await db.execute(
            select(TeachClass).where(TeachClass.class_no == class_no, TeachClass.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def add_teach_class(cls, db: AsyncSession, class_obj: TeachClass):
        db.add(class_obj)
        await db.flush()
        await db.refresh(class_obj)
        return class_obj

    @classmethod
    async def edit_teach_class(cls, db: AsyncSession, class_obj: TeachClass):
        class_obj.update_time = datetime.now()
        await db.flush()
        return class_obj

    @classmethod
    async def delete_teach_class(cls, db: AsyncSession, class_ids: list[int], update_by: str):
        await db.execute(
            update(TeachClass)
            .where(TeachClass.id.in_(class_ids), TeachClass.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )
        await db.execute(
            update(TeachClassStudent)
            .where(TeachClassStudent.class_id.in_(class_ids), TeachClassStudent.del_flag == 0)
            .values(status=2, del_flag=1, update_by=update_by, update_time=datetime.now())
        )
        await db.execute(
            update(TeachClassTeacher)
            .where(TeachClassTeacher.class_id.in_(class_ids), TeachClassTeacher.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def update_teach_class_recharge(cls, db: AsyncSession, class_id: int, allow_recharge: int, update_by: str):
        await db.execute(
            update(TeachClass)
            .where(TeachClass.id == class_id, TeachClass.del_flag == 0)
            .values(allow_recharge=allow_recharge, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def add_class_teacher(cls, db: AsyncSession, teacher_relation: TeachClassTeacher):
        db.add(teacher_relation)
        await db.flush()
        await db.refresh(teacher_relation)
        return teacher_relation

    @classmethod
    async def delete_class_teachers(cls, db: AsyncSession, class_id: int, update_by: str):
        await db.execute(
            update(TeachClassTeacher)
            .where(TeachClassTeacher.class_id == class_id, TeachClassTeacher.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def get_active_class_student(cls, db: AsyncSession, class_id: int, student_id: int):
        result = await db.execute(
            select(TeachClassStudent).where(
                TeachClassStudent.class_id == class_id,
                TeachClassStudent.student_id == student_id,
                TeachClassStudent.status == 1,
                TeachClassStudent.del_flag == 0,
            )
        )
        return result.scalars().first()

    @classmethod
    async def get_class_student_any(cls, db: AsyncSession, class_id: int, student_id: int):
        result = await db.execute(
            select(TeachClassStudent).where(
                TeachClassStudent.class_id == class_id,
                TeachClassStudent.student_id == student_id,
            )
        )
        return result.scalars().first()

    @classmethod
    async def add_class_student(cls, db: AsyncSession, class_student: TeachClassStudent):
        db.add(class_student)
        await db.flush()
        await db.refresh(class_student)
        return class_student

    @classmethod
    async def edit_class_student(cls, db: AsyncSession, class_student: TeachClassStudent):
        class_student.update_time = datetime.now()
        await db.flush()
        return class_student

    @classmethod
    async def remove_class_students(cls, db: AsyncSession, class_id: int, student_ids: list[int], update_by: str):
        await db.execute(
            update(TeachClassStudent)
            .where(
                TeachClassStudent.class_id == class_id,
                TeachClassStudent.student_id.in_(student_ids),
                TeachClassStudent.status == 1,
                TeachClassStudent.del_flag == 0,
            )
            .values(status=2, leave_date=datetime.now().date(), update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def refresh_class_student_count(cls, db: AsyncSession, class_id: int):
        count_result = await db.execute(
            select(func.count(TeachClassStudent.id)).where(
                TeachClassStudent.class_id == class_id,
                TeachClassStudent.status == 1,
                TeachClassStudent.del_flag == 0,
            )
        )
        current_students = count_result.scalar() or 0
        enroll_status = 1
        class_obj = await cls.get_teach_class_by_id(db, class_id)
        if class_obj and class_obj.max_students and current_students >= class_obj.max_students:
            enroll_status = 2
        await db.execute(
            update(TeachClass)
            .where(TeachClass.id == class_id, TeachClass.del_flag == 0)
            .values(current_students=current_students, enroll_status=enroll_status, update_time=datetime.now())
        )
        return current_students

    @classmethod
    async def get_class_students(cls, db: AsyncSession, class_id: int):
        result = await db.execute(
            select(TeachClassStudent, TeachStudent, TeachBaseUser, TeachStudentCourseAccount)
            .join(TeachStudent, TeachClassStudent.student_id == TeachStudent.id)
            .join(TeachParent, TeachStudent.parent_id == TeachParent.id)
            .join(TeachBaseUser, TeachParent.user_id == TeachBaseUser.id)
            .outerjoin(TeachStudentCourseAccount, TeachClassStudent.course_account_id == TeachStudentCourseAccount.id)
            .where(
                TeachClassStudent.class_id == class_id,
                TeachClassStudent.status == 1,
                TeachClassStudent.del_flag == 0,
                TeachStudent.del_flag == 0,
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0,
            )
            .order_by(desc(TeachClassStudent.join_date), desc(TeachClassStudent.id))
        )
        return result.all()

    @classmethod
    async def get_available_students(cls, db: AsyncSession, class_obj: TeachClass, keyword: str | None = None):
        active_member_exists = (
            select(TeachClassStudent.id)
            .where(
                TeachClassStudent.class_id == class_obj.id,
                TeachClassStudent.student_id == TeachStudent.id,
                TeachClassStudent.status == 1,
                TeachClassStudent.del_flag == 0,
            )
            .exists()
        )
        account_conditions = [
            TeachStudentCourseAccount.student_id == TeachStudent.id,
            TeachStudentCourseAccount.course_id == class_obj.course_id,
            TeachStudentCourseAccount.del_flag == 0,
            TeachStudentCourseAccount.status == 'active',
        ]
        query = (
            select(TeachStudent, TeachBaseUser, TeachStudentCourseAccount)
            .join(TeachParent, TeachStudent.parent_id == TeachParent.id)
            .join(TeachBaseUser, TeachParent.user_id == TeachBaseUser.id)
            .outerjoin(TeachStudentCourseAccount, and_(*account_conditions))
            .where(
                TeachStudent.del_flag == 0,
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0,
                ~active_member_exists,
            )
        )
        if keyword:
            query = query.where(or_(TeachStudent.student_name.like(f'%{keyword}%'), TeachBaseUser.phone.like(f'%{keyword}%')))
        query = query.order_by(desc(TeachStudent.create_time), desc(TeachStudent.id))
        result = await db.execute(query)
        return result.all()

    @classmethod
    async def get_student_course_account(cls, db: AsyncSession, student_id: int, course_id: int):
        result = await db.execute(
            select(TeachStudentCourseAccount)
            .where(
                TeachStudentCourseAccount.student_id == student_id,
                TeachStudentCourseAccount.course_id == course_id,
                TeachStudentCourseAccount.status == 'active',
                TeachStudentCourseAccount.del_flag == 0,
            )
            .order_by(desc(TeachStudentCourseAccount.create_time), desc(TeachStudentCourseAccount.id))
        )
        return result.scalars().first()

    @classmethod
    async def get_teacher_by_id(cls, db: AsyncSession, teacher_id: int):
        result = await db.execute(
            select(TeachTeacher).where(TeachTeacher.id == teacher_id, TeachTeacher.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def get_course_account_by_id(cls, db: AsyncSession, account_id: int):
        result = await db.execute(
            select(TeachStudentCourseAccount).where(
                TeachStudentCourseAccount.id == account_id,
                TeachStudentCourseAccount.del_flag == 0,
            )
        )
        return result.scalars().first()

    @classmethod
    async def add_class_attendance(cls, db: AsyncSession, attendance: TeachClassAttendance):
        db.add(attendance)
        await db.flush()
        await db.refresh(attendance)
        return attendance

    @classmethod
    async def get_class_attendance_by_event_id(cls, db: AsyncSession, event_id: int):
        result = await db.execute(
            select(TeachClassAttendance).where(
                TeachClassAttendance.event_id == event_id,
                TeachClassAttendance.del_flag == 0,
            )
        )
        return result.scalars().first()

    @classmethod
    async def add_class_attendance_detail(cls, db: AsyncSession, detail: TeachClassAttendanceDetail):
        db.add(detail)
        await db.flush()
        return detail

    @classmethod
    async def get_class_attendance_list(cls, db: AsyncSession, class_id: int):
        result = await db.execute(
            select(TeachClassAttendance)
            .where(
                TeachClassAttendance.class_id == class_id,
                TeachClassAttendance.del_flag == 0,
            )
            .order_by(desc(TeachClassAttendance.class_date), desc(TeachClassAttendance.id))
        )
        return result.scalars().all()

    @classmethod
    async def get_class_attendance_detail(cls, db: AsyncSession, attendance_id: int):
        result = await db.execute(
            select(TeachClassAttendance, TeachClassAttendanceDetail, TeachStudent, TeachBaseUser)
            .join(
                TeachClassAttendanceDetail,
                TeachClassAttendanceDetail.attendance_id == TeachClassAttendance.id,
            )
            .join(TeachStudent, TeachClassAttendanceDetail.student_id == TeachStudent.id)
            .join(TeachParent, TeachStudent.parent_id == TeachParent.id)
            .join(TeachBaseUser, TeachParent.user_id == TeachBaseUser.id)
            .where(
                TeachClassAttendance.id == attendance_id,
                TeachClassAttendance.del_flag == 0,
                TeachClassAttendanceDetail.del_flag == 0,
                TeachStudent.del_flag == 0,
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0,
            )
            .order_by(TeachClassAttendanceDetail.id)
        )
        return result.all()
