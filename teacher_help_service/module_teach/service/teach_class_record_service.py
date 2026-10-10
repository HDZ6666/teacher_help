from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
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
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil
from utils.page_util import PageResponseModel


class TeachClassRecordService:
    # 导出单次最多行数，超出请缩小查询条件（避免一次性拉取全表）
    EXPORT_MAX_ROWS = 10000

    EXPORT_MAPPINGS = {
        'attendance': {
            'attendanceTime': '点名时间',
            'classTime': '上课时间',
            'className': '班级名称',
            'courseName': '授课课程',
            'teacherName': '上课老师',
            'lessonHoursText': '授课课时',
            'expectedCount': '应到人数',
            'actualCount': '实到人数',
            'attendanceRate': '出勤率(%)',
            'deductedQuantity': '扣课合计',
            'classroom': '上课教室',
            'content': '上课内容',
            'statusName': '状态',
        },
        'overtime': {
            'classDate': '上课日期',
            'classTime': '上课时间',
            'className': '班级名称',
            'teacherName': '上课老师',
            'courseName': '授课课程',
            'classroom': '上课教室',
            'classContent': '上课内容',
            'statusName': '状态',
        },
        'makeup': {
            'studentName': '学员姓名',
            'phone': '手机号',
            'className': '班级名称',
            'classDate': '上课日期',
            'classTime': '上课时间',
            'teacherName': '上课老师',
            'courseName': '课程',
            'makeupStatus': '缺课状态',
            'consumeType': '消耗方式',
            'shouldDeduct': '应扣额度',
            'actualDeduct': '实扣额度',
            'madeupStatusName': '补课状态',
            'makeupTime': '标记已补时间',
            'makeupDetail': '补课说明',
            'classContent': '上课内容',
        },
        'absence': {
            'studentName': '学员',
            'phone': '手机号',
            'className': '所在班级',
            'absenceCount': '未到次数',
            'leaveCount': '请假次数',
            'missedCount': '缺课合计',
            'missedClasses': '未上课天数',
            'lastClassDate': '上次上课日期',
        },
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
            'madeupStatus': bool(detail.makeup_flag),
            'madeupStatusName': '已补课' if detail.makeup_flag else '未补',
            'makeupTime': detail.makeup_time,
            'makeupBy': detail.makeup_by or '',
            'makeupDetail': detail.makeup_remark or '',
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

    @classmethod
    async def export_record_list_services(cls, query_db: AsyncSession, record_type: str, query_object):
        """
        按当前查询条件导出上课记录（点名记录/超时未点名/补课/缺课提醒）Excel，最多 EXPORT_MAX_ROWS 行
        """
        list_services = {
            'attendance': cls.get_attendance_list_services,
            'overtime': cls.get_overtime_list_services,
            'makeup': cls.get_makeup_list_services,
            'absence': cls.get_absence_list_services,
        }
        if record_type not in list_services:
            raise ServiceException(message='不支持的导出类型')
        query_object.page_num = 1
        query_object.page_size = cls.EXPORT_MAX_ROWS
        page = await list_services[record_type](query_db, query_object)
        return ExcelUtil.export_list2excel(page.rows, cls.EXPORT_MAPPINGS[record_type])

    @classmethod
    async def mark_makeup_services(cls, query_db: AsyncSession, ids: list, remark: str, operator: str):
        """
        缺课明细标记已补：只记录补课标记，不改变扣课、课程账户与考勤状态；已标记的跳过（幂等）
        """
        unique_ids = sorted(set(ids))
        rows = (
            await query_db.execute(
                select(TeachClassAttendanceDetail, TeachClassAttendance)
                .join(TeachClassAttendance, TeachClassAttendanceDetail.attendance_id == TeachClassAttendance.id)
                .where(TeachClassAttendanceDetail.id.in_(unique_ids))
            )
        ).all()
        found = {detail.id: (detail, attendance) for detail, attendance in rows}
        missing = [item for item in unique_ids if item not in found]
        if missing:
            raise ServiceException(message=f'缺课记录不存在：{missing}')
        for detail, attendance in found.values():
            if detail.del_flag != 0 or attendance.del_flag != 0:
                raise ServiceException(message=f'{detail.student_name} 的点名记录已撤销，不能标记已补')
            if detail.status not in [3, 4]:
                raise ServiceException(message=f'{detail.student_name} 该次不是请假/未到，无需补课')
        marked = 0
        now = datetime.now()
        try:
            for detail, _ in found.values():
                if detail.makeup_flag:
                    continue
                detail.makeup_flag = 1
                detail.makeup_time = now
                detail.makeup_by = operator
                detail.makeup_remark = remark
                detail.update_by = operator
                detail.update_time = now
                marked += 1
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise e
        skipped = len(found) - marked
        message = f'已标记 {marked} 条为已补课' + (f'，{skipped} 条此前已标记' if skipped else '')
        return CrudResponseModel(is_success=True, message=message, result={'marked': marked, 'skipped': skipped})
