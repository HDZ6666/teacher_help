from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_teach.dao.teach_class_record_dao import TeachClassRecordDao
from module_teach.entity.do.teach_class_do import TeachClassAttendance, TeachClassAttendanceDetail
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.vo.teach_class_record_vo import (
    ClassRecordAbsenceQueryModel,
    ClassRecordAttendanceQueryModel,
    ClassRecordMakeupQueryModel,
    ClassRecordOvertimeQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachClassRecordService:
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
    def format_decimal_text(cls, value):
        if value in [None, '']:
            return '0'
        decimal_value = Decimal(str(value))
        if decimal_value == decimal_value.to_integral():
            return str(int(decimal_value))
        return format(decimal_value.normalize(), 'f').rstrip('0').rstrip('.')

    @classmethod
    def format_attendance_row(cls, attendance: TeachClassAttendance):
        row = CamelCaseUtil.transform_result(attendance)
        actual_count = (attendance.present_count or 0) + (attendance.late_count or 0)
        expected_count = attendance.student_count or 0
        row.update(
            {
                'attendanceTime': attendance.create_time,
                'classTime': f'{attendance.class_date} {attendance.start_time}~{attendance.end_time}',
                'expectedCount': expected_count,
                'actualCount': actual_count,
                'duration': attendance.lesson_hours,
                'lessonHoursText': f'{cls.format_decimal_text(attendance.lesson_hours)}课时',
                'attendanceRate': round(actual_count / expected_count * 100, 2) if expected_count else 0,
                'statusName': '正常' if attendance.status == 1 else '异常',
            }
        )
        return row

    @classmethod
    def format_attendance_detail_row(cls, detail: TeachClassAttendanceDetail, student, base_user):
        row = CamelCaseUtil.transform_result(detail)
        status_name = cls.ATTENDANCE_STATUS_LABELS.get(detail.status, '-')
        row.update(
            {
                'studentName': student.student_name,
                'phone': base_user.phone,
                'statusName': status_name,
                'consumeType': detail.consume_method,
                'makeupStatus': '待补课' if detail.status in [3, 4] else '-',
                'quota': f'{cls.format_decimal_text(detail.deduct_quantity)}课时',
            }
        )
        return row

    @classmethod
    async def get_attendance_list_services(
        cls, query_db: AsyncSession, query_object: ClassRecordAttendanceQueryModel
    ):
        rows, total = await TeachClassRecordDao.get_attendance_list(query_db, query_object)
        return cls.make_page(
            [cls.format_attendance_row(row) for row in rows],
            total,
            query_object.page_num,
            query_object.page_size,
        )

    @classmethod
    async def get_attendance_detail_services(cls, query_db: AsyncSession, record_id: int):
        rows = await TeachClassRecordDao.get_attendance_detail(query_db, record_id)
        if not rows:
            raise ServiceException(message='点名记录不存在')
        attendance = rows[0][0]
        details = [cls.format_attendance_detail_row(detail, student, base_user) for _, detail, student, base_user in rows]
        return {**cls.format_attendance_row(attendance), 'details': details}

    @classmethod
    def format_makeup_row(cls, attendance, detail, student, base_user):
        status_name = cls.ATTENDANCE_STATUS_LABELS.get(detail.status, '-')
        return {
            'id': detail.id,
            'attendanceId': attendance.id,
            'classId': attendance.class_id,
            'studentId': student.id,
            'studentName': student.student_name,
            'phone': base_user.phone,
            'className': attendance.class_name,
            'classDate': attendance.class_date,
            'classTime': f'{attendance.start_time}~{attendance.end_time}',
            'teacherName': attendance.teacher_name,
            'courseName': attendance.course_name,
            'makeupStatus': status_name,
            'status': detail.status,
            'statusName': status_name,
            'consumeType': detail.consume_method or '-',
            'shouldDeduct': f'{cls.format_decimal_text(attendance.lesson_hours)}课时',
            'actualDeduct': f'{cls.format_decimal_text(detail.deduct_quantity)}课时',
            'deductQuantity': detail.deduct_quantity,
            'madeupStatus': False,
            'makeupDetail': '',
            'classContent': attendance.content,
        }

    @classmethod
    async def get_makeup_list_services(cls, query_db: AsyncSession, query_object: ClassRecordMakeupQueryModel):
        rows, total = await TeachClassRecordDao.get_makeup_list(query_db, query_object)
        return cls.make_page(
            [cls.format_makeup_row(attendance, detail, student, base_user) for attendance, detail, student, base_user in rows],
            total,
            query_object.page_num,
            query_object.page_size,
        )

    @classmethod
    def format_absence_row(cls, row):
        mapping = row._mapping
        last_class_date = mapping.get('last_class_date')
        missed_days = (date.today() - last_class_date).days if last_class_date else None
        return {
            'id': f"{mapping.get('student_id')}-{mapping.get('class_id')}",
            'studentId': mapping.get('student_id'),
            'studentName': mapping.get('student_name'),
            'phone': mapping.get('phone'),
            'classId': mapping.get('class_id'),
            'className': mapping.get('class_name'),
            'absenceCount': mapping.get('absence_count') or 0,
            'leaveCount': mapping.get('leave_count') or 0,
            'missedClasses': missed_days,
            'missedCount': mapping.get('missed_count') or 0,
            'restrictedBy': '',
            'advisor': '',
            'lastClassDate': last_class_date,
            'lastRemindTime': '',
        }

    @classmethod
    async def get_absence_list_services(cls, query_db: AsyncSession, query_object: ClassRecordAbsenceQueryModel):
        rows, total = await TeachClassRecordDao.get_absence_list(query_db, query_object)
        return cls.make_page(
            [cls.format_absence_row(row) for row in rows],
            total,
            query_object.page_num,
            query_object.page_size,
        )

    @classmethod
    def format_overtime_row(cls, event: TeachScheduleEvent, teacher=None):
        row = CamelCaseUtil.transform_result(event)
        row.update(
            {
                'classDate': event.event_date,
                'classTime': f'{event.start_time.strftime("%H:%M")}~{event.end_time.strftime("%H:%M")}',
                'teacherName': teacher.teacher_name if teacher else row.get('teacherName') or '',
                'classContent': event.content,
                'statusName': '超时未点',
            }
        )
        return row

    @classmethod
    async def get_overtime_list_services(cls, query_db: AsyncSession, query_object: ClassRecordOvertimeQueryModel):
        rows, total = await TeachClassRecordDao.get_overtime_list(query_db, query_object)
        return cls.make_page(
            [cls.format_overtime_row(event, teacher) for event, teacher in rows],
            total,
            query_object.page_num,
            query_object.page_size,
        )
