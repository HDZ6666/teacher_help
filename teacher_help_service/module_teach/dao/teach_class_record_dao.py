from datetime import datetime

from sqlalchemy import and_, case, desc, exists, func, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.do.teach_class_do import TeachClassAttendance, TeachClassAttendanceDetail
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from module_teach.entity.vo.teach_class_record_vo import (
    ClassRecordAbsenceQueryModel,
    ClassRecordAttendanceQueryModel,
    ClassRecordMakeupQueryModel,
    ClassRecordOvertimeQueryModel,
)


class TeachClassRecordDao:
    @classmethod
    async def paginate(cls, db: AsyncSession, query, page_num: int, page_size: int):
        total = (await db.execute(select(func.count()).select_from(query.order_by(None).subquery()))).scalar() or 0
        result = await db.execute(query.offset((page_num - 1) * page_size).limit(page_size))
        return result.all(), total

    @classmethod
    async def get_attendance_list(cls, db: AsyncSession, query_object: ClassRecordAttendanceQueryModel):
        query = select(TeachClassAttendance).where(TeachClassAttendance.del_flag == 0)
        if query_object.class_id:
            query = query.where(TeachClassAttendance.class_id == query_object.class_id)
        if query_object.course_id:
            query = query.where(TeachClassAttendance.course_id == query_object.course_id)
        if query_object.teacher_id:
            query = query.where(TeachClassAttendance.teacher_id == query_object.teacher_id)
        if query_object.status is not None:
            query = query.where(TeachClassAttendance.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachClassAttendance.class_date >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachClassAttendance.class_date <= query_object.end_time)
        query = query.order_by(desc(TeachClassAttendance.class_date), desc(TeachClassAttendance.id))
        rows, total = await cls.paginate(db, query, query_object.page_num, query_object.page_size)
        return [row[0] for row in rows], total

    @classmethod
    async def get_attendance_detail(cls, db: AsyncSession, record_id: int):
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
                TeachClassAttendance.id == record_id,
                TeachClassAttendance.del_flag == 0,
                TeachClassAttendanceDetail.del_flag == 0,
                TeachStudent.del_flag == '0',
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0,
            )
            .order_by(TeachClassAttendanceDetail.id)
        )
        return result.all()

    @classmethod
    async def get_makeup_list(cls, db: AsyncSession, query_object: ClassRecordMakeupQueryModel):
        query = (
            select(TeachClassAttendance, TeachClassAttendanceDetail, TeachStudent, TeachBaseUser)
            .join(
                TeachClassAttendanceDetail,
                TeachClassAttendanceDetail.attendance_id == TeachClassAttendance.id,
            )
            .join(TeachStudent, TeachClassAttendanceDetail.student_id == TeachStudent.id)
            .join(TeachParent, TeachStudent.parent_id == TeachParent.id)
            .join(TeachBaseUser, TeachParent.user_id == TeachBaseUser.id)
            .where(
                TeachClassAttendance.del_flag == 0,
                TeachClassAttendanceDetail.del_flag == 0,
                TeachClassAttendanceDetail.status.in_([3, 4]),
                TeachStudent.del_flag == '0',
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0,
            )
        )
        if query_object.student_keyword:
            keyword = f'%{query_object.student_keyword}%'
            query = query.where(or_(TeachStudent.student_name.like(keyword), TeachBaseUser.phone.like(keyword)))
        if query_object.class_id:
            query = query.where(TeachClassAttendance.class_id == query_object.class_id)
        if query_object.course_id:
            query = query.where(TeachClassAttendance.course_id == query_object.course_id)
        if query_object.teacher_id:
            query = query.where(TeachClassAttendance.teacher_id == query_object.teacher_id)
        if query_object.begin_time:
            query = query.where(TeachClassAttendance.class_date >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachClassAttendance.class_date <= query_object.end_time)
        query = query.order_by(desc(TeachClassAttendance.class_date), desc(TeachClassAttendanceDetail.id))
        return await cls.paginate(db, query, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_absence_list(cls, db: AsyncSession, query_object: ClassRecordAbsenceQueryModel):
        absent_count = func.sum(case((TeachClassAttendanceDetail.status == 4, 1), else_=0)).label('absence_count')
        leave_count = func.sum(case((TeachClassAttendanceDetail.status == 3, 1), else_=0)).label('leave_count')
        missed_count = func.sum(case((TeachClassAttendanceDetail.status.in_([3, 4]), 1), else_=0)).label(
            'missed_count'
        )
        last_class_date = func.max(TeachClassAttendance.class_date).label('last_class_date')
        query = (
            select(
                TeachClassAttendanceDetail.student_id.label('student_id'),
                TeachStudent.student_name.label('student_name'),
                TeachBaseUser.phone.label('phone'),
                TeachClassAttendanceDetail.class_id.label('class_id'),
                TeachClassAttendance.class_name.label('class_name'),
                absent_count,
                leave_count,
                missed_count,
                last_class_date,
            )
            .join(TeachClassAttendance, TeachClassAttendanceDetail.attendance_id == TeachClassAttendance.id)
            .join(TeachStudent, TeachClassAttendanceDetail.student_id == TeachStudent.id)
            .join(TeachParent, TeachStudent.parent_id == TeachParent.id)
            .join(TeachBaseUser, TeachParent.user_id == TeachBaseUser.id)
            .where(
                TeachClassAttendance.del_flag == 0,
                TeachClassAttendanceDetail.del_flag == 0,
                TeachClassAttendanceDetail.status.in_([3, 4]),
                TeachStudent.del_flag == '0',
                TeachParent.del_flag == 0,
                TeachBaseUser.del_flag == 0,
            )
            .group_by(
                TeachClassAttendanceDetail.student_id,
                TeachStudent.student_name,
                TeachBaseUser.phone,
                TeachClassAttendanceDetail.class_id,
                TeachClassAttendance.class_name,
            )
        )
        if query_object.student_keyword:
            keyword = f'%{query_object.student_keyword}%'
            query = query.where(or_(TeachStudent.student_name.like(keyword), TeachBaseUser.phone.like(keyword)))
        if query_object.class_id:
            query = query.where(TeachClassAttendanceDetail.class_id == query_object.class_id)
        having_conditions = []
        if query_object.min_absences is not None:
            having_conditions.append(missed_count >= query_object.min_absences)
        if query_object.max_absences is not None:
            having_conditions.append(missed_count <= query_object.max_absences)
        if having_conditions:
            query = query.having(and_(*having_conditions))
        query = query.order_by(desc(missed_count), desc(last_class_date))
        return await cls.paginate(db, query, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_overtime_list(cls, db: AsyncSession, query_object: ClassRecordOvertimeQueryModel):
        attended_exists = exists().where(
            TeachClassAttendance.event_id == TeachScheduleEvent.id,
            TeachClassAttendance.del_flag == 0,
        )
        query = (
            select(TeachScheduleEvent, TeachTeacher)
            .outerjoin(TeachTeacher, TeachScheduleEvent.teacher_id == TeachTeacher.id)
            .where(
                TeachScheduleEvent.del_flag == '0',
                TeachScheduleEvent.status.in_(['0', '1']),
                TeachScheduleEvent.end_time < datetime.now(),
                not_(attended_exists),
            )
            .order_by(desc(TeachScheduleEvent.event_date), desc(TeachScheduleEvent.start_time))
        )
        if query_object.class_id:
            query = query.where(TeachScheduleEvent.class_id == query_object.class_id)
        if query_object.course_id:
            query = query.where(TeachScheduleEvent.course_id == query_object.course_id)
        if query_object.teacher_id:
            query = query.where(TeachScheduleEvent.teacher_id == query_object.teacher_id)
        if query_object.begin_time:
            query = query.where(TeachScheduleEvent.event_date >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachScheduleEvent.event_date <= query_object.end_time)
        return await cls.paginate(db, query, query_object.page_num, query_object.page_size)
