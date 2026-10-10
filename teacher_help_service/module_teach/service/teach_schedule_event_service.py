from datetime import datetime
from decimal import Decimal
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_schedule_attendance_dao import TeachScheduleAttendanceDao
from module_teach.dao.teach_schedule_event_dao import TeachScheduleEventDao
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.vo.teach_schedule_event_vo import (
    AddTeachScheduleEventModel,
    CalendarQueryModel,
    DeleteTeachScheduleEventModel,
    EditTeachScheduleEventModel,
    TeachScheduleEventDetailModel,
    TeachScheduleEventPageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachScheduleEventService:
    """
    排课事件管理模块服务层
    """

    STATUS_LABELS = {
        '0': '已安排',
        '1': '进行中',
        '2': '已完成',
        '3': '已取消',
    }

    @classmethod
    def to_decimal(cls, value, default=1):
        if value in [None, '']:
            return Decimal(str(default))
        return Decimal(str(value)).quantize(Decimal('0.01'))

    @classmethod
    def get_row_part(cls, row: Any, index: int):
        item = None
        if isinstance(row, (list, tuple)) and len(row) > index:
            item = row[index]
        else:
            try:
                item = row[index]
            except (KeyError, IndexError, TypeError):
                return {}
        if item is None:
            return {}
        if isinstance(item, dict):
            return item
        return CamelCaseUtil.transform_result(item)

    @classmethod
    def format_event_row(cls, row: Any):
        event = cls.get_row_part(row, 0)
        teacher = cls.get_row_part(row, 1)
        course = cls.get_row_part(row, 2)
        if not isinstance(event, dict):
            event = {}
        if not isinstance(teacher, dict):
            teacher = {}
        if not isinstance(course, dict):
            course = {}

        course_name = event.get('courseName') or course.get('courseName') or event.get('subjectCode')
        class_name = event.get('className') or '-'
        row_data = {
            **event,
            'teacherName': teacher.get('teacherName') or event.get('teacherName'),
            'className': class_name,
            'courseName': course_name,
            'scheduleColor': course.get('scheduleColor') or '#409EFF',
            'statusName': cls.STATUS_LABELS.get(str(event.get('status')), event.get('status')),
        }
        return row_data

    @classmethod
    async def get_teach_schedule_event_list_services(
        cls,
        request,
        query_db: AsyncSession,
        query_object: TeachScheduleEventPageQueryModel,
        data_scope_sql: str,
        is_page: bool = False,
    ):
        """
        获取排课事件列表信息service
        """
        event_list_result = await TeachScheduleEventDao.get_teach_schedule_event_list(
            query_db, query_object, data_scope_sql, is_page
        )

        if is_page:
            rows = [cls.format_event_row(row) for row in event_list_result.rows]
            return PageResponseModel(
                **{
                    **event_list_result.model_dump(by_alias=True),
                    'rows': rows,
                }
            )
        return [cls.format_event_row(row) for row in event_list_result]

    @classmethod
    def export_schedule_event_list_services(cls, event_rows: list):
        """
        导出课表（课次列表）为 Excel 二进制
        """
        from utils.excel_util import ExcelUtil

        mapping_dict = {
            'eventDate': '上课日期',
            'timeRange': '上课时间',
            'className': '班级',
            'courseName': '课程',
            'teacherName': '上课老师',
            'classroom': '上课教室',
            'lessonHours': '课时',
            'statusName': '状态',
            'cachedPlanned': '应到人数',
            'cachedPresent': '出勤人数',
            'cachedExcused': '请假人数',
            'cachedAbsent': '缺勤人数',
            'remark': '备注',
        }
        rows = []
        for row in event_rows:
            item = dict(row)
            start, end = str(item.get('startTime') or ''), str(item.get('endTime') or '')
            item['timeRange'] = f'{start.replace("T", " ")[11:16]}-{end.replace("T", " ")[11:16]}'
            rows.append(item)
        return ExcelUtil.export_list2excel(rows, mapping_dict)

    @classmethod
    async def get_teach_schedule_event_detail_services(
        cls,
        request,
        query_db: AsyncSession,
        event_id: int,
    ):
        """
        获取排课事件详情service
        """
        event_result = await TeachScheduleEventDao.get_teach_schedule_event_by_id(query_db, event_id)
        if not event_result:
            return TeachScheduleEventDetailModel()

        detail_data = cls.format_event_row(event_result)
        detail = TeachScheduleEventDetailModel(**detail_data)
        attendance_with_students = await TeachScheduleAttendanceDao.get_attendances_with_students_by_event(
            query_db, event_id
        )
        students = []
        for att, student in attendance_with_students:
            students.append(
                {
                    'studentId': student.id,
                    'studentName': student.student_name,
                    'status': att.status,
                    'statusName': cls.get_attendance_status_name(att.status),
                    'checkInTime': att.check_in_time,
                    'notes': att.notes,
                }
            )
        detail.students = students
        return detail

    @classmethod
    def get_attendance_status_name(cls, status: int):
        return {
            0: '未到',
            1: '出勤',
            2: '迟到',
            3: '请假',
            4: '缺勤',
        }.get(status, '-')

    @classmethod
    async def get_schedule_members(cls, query_db: AsyncSession, class_id: int, student_ids: list[int] | None = None):
        member_rows = await TeachClassDao.get_class_students(query_db, class_id)
        member_map = {class_student.student_id: class_student for class_student, _, _, _ in member_rows}
        if student_ids is None:
            return list(member_map.keys())

        normalized_student_ids = sorted(set(student_ids))
        missing_ids = [student_id for student_id in normalized_student_ids if student_id not in member_map]
        if missing_ids:
            raise ServiceException(message='排课学员不属于当前班级')
        return normalized_student_ids

    @classmethod
    async def validate_schedule_base(
        cls,
        query_db: AsyncSession,
        class_id: int,
        course_id: int,
        teacher_id: int,
        start_time: datetime,
        end_time: datetime,
        classroom: str | None,
        exclude_event_id: int | None = None,
    ):
        if end_time <= start_time:
            raise ServiceException(message='结束时间必须晚于开始时间')

        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        if class_obj.status != 1:
            raise ServiceException(message='班级已停用，不能排课')

        course = await TeachCourseDao.get_teach_course_by_id(query_db, course_id)
        if not course or course.status != 1:
            raise ServiceException(message='课程不存在或已停用')
        if class_obj.course_id != course.id:
            raise ServiceException(message='排课课程必须和班级关联课程一致')

        teacher = await TeachClassDao.get_teacher_by_id(query_db, teacher_id)
        if not teacher:
            raise ServiceException(message='上课老师不存在')

        classroom = classroom or class_obj.classroom
        conflict_labels = await TeachScheduleEventDao.has_resource_conflict(
            query_db,
            start_time,
            end_time,
            teacher_id=teacher_id,
            class_id=class_id,
            classroom=classroom,
            exclude_event_id=exclude_event_id,
        )
        if conflict_labels:
            raise ServiceException(message=f"{'、'.join(conflict_labels)}在该时间段存在冲突")
        return class_obj, course, teacher

    @classmethod
    async def refresh_class_total_lessons(cls, query_db: AsyncSession, class_id: int | None):
        if not class_id:
            return
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            return
        class_obj.total_lessons = await TeachScheduleEventDao.count_class_events(query_db, class_id)
        class_obj.update_time = datetime.now()

    @classmethod
    async def add_teach_schedule_event_services(
        cls,
        query_db: AsyncSession,
        add_event: AddTeachScheduleEventModel,
        current_user: str,
    ):
        """
        新增排课事件service
        """
        classroom = add_event.classroom
        class_obj, course, teacher = await cls.validate_schedule_base(
            query_db,
            add_event.class_id,
            add_event.course_id,
            add_event.teacher_id,
            add_event.start_time,
            add_event.end_time,
            classroom,
        )
        classroom = classroom or class_obj.classroom
        student_ids = await cls.get_schedule_members(query_db, class_obj.id, add_event.student_ids)
        try:
            event = TeachScheduleEvent(
                teacher_id=teacher.id,
                course_id=course.id,
                course_name=course.course_name,
                class_id=class_obj.id,
                class_name=class_obj.class_name,
                subject_code=course.subject or add_event.subject_code,
                start_time=add_event.start_time,
                end_time=add_event.end_time,
                event_date=add_event.start_time.date(),
                classroom=classroom,
                lesson_hours=cls.to_decimal(add_event.lesson_hours, class_obj.lesson_hours or 1),
                content=add_event.content,
                status='0',
                cached_planned=len(student_ids),
                create_by=current_user,
                update_by=current_user,
                remark=add_event.remark,
            )
            event_id = await TeachScheduleEventDao.add_teach_schedule_event(query_db, event)
            await cls.save_event_attendances(query_db, event_id, student_ids, current_user)
            await cls.refresh_class_total_lessons(query_db, class_obj.id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='排课成功', result={'id': event_id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def save_event_attendances(
        cls,
        query_db: AsyncSession,
        event_id: int,
        student_ids: list[int],
        current_user: str,
    ):
        attendances = [
            TeachScheduleAttendance(
                event_id=event_id,
                student_id=student_id,
                status=0,
                is_countable=1,
                create_by=current_user,
                update_by=current_user,
            )
            for student_id in student_ids
        ]
        if attendances:
            await TeachScheduleAttendanceDao.batch_add_attendances(query_db, attendances)

    @classmethod
    async def edit_teach_schedule_event_services(
        cls,
        query_db: AsyncSession,
        edit_event: EditTeachScheduleEventModel,
        current_user: str,
    ):
        """
        编辑排课事件service
        """
        event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, edit_event.id)
        if not event:
            raise ServiceException(message='排课事件不存在')

        class_id = edit_event.class_id or event.class_id
        course_id = edit_event.course_id or event.course_id
        teacher_id = edit_event.teacher_id or event.teacher_id
        start_time = edit_event.start_time or event.start_time
        end_time = edit_event.end_time or event.end_time
        classroom = edit_event.classroom if edit_event.classroom is not None else event.classroom
        old_class_id = event.class_id

        class_obj, course, teacher = await cls.validate_schedule_base(
            query_db,
            class_id,
            course_id,
            teacher_id,
            start_time,
            end_time,
            classroom,
            exclude_event_id=edit_event.id,
        )
        student_ids = (
            await cls.get_schedule_members(query_db, class_obj.id, edit_event.student_ids)
            if edit_event.student_ids is not None or old_class_id != class_obj.id
            else None
        )

        try:
            event.teacher_id = teacher.id
            event.course_id = course.id
            event.course_name = course.course_name
            event.class_id = class_obj.id
            event.class_name = class_obj.class_name
            event.subject_code = course.subject or edit_event.subject_code or event.subject_code
            event.start_time = start_time
            event.end_time = end_time
            event.event_date = start_time.date()
            event.classroom = classroom or class_obj.classroom
            if edit_event.lesson_hours is not None:
                event.lesson_hours = cls.to_decimal(edit_event.lesson_hours, class_obj.lesson_hours or 1)
            if edit_event.content is not None:
                event.content = edit_event.content
            if edit_event.status is not None:
                event.status = edit_event.status
            if edit_event.remark is not None:
                event.remark = edit_event.remark
            event.update_by = current_user
            event.update_time = datetime.now()
            await TeachScheduleEventDao.edit_teach_schedule_event(query_db, event)
            if student_ids is not None:
                await TeachScheduleAttendanceDao.delete_attendances_by_event(query_db, edit_event.id)
                await cls.save_event_attendances(query_db, edit_event.id, student_ids, current_user)
                event.cached_planned = len(student_ids)
            await cls.refresh_class_total_lessons(query_db, old_class_id)
            await cls.refresh_class_total_lessons(query_db, class_obj.id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='修改成功', result={'id': edit_event.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_schedule_event_services(
        cls,
        query_db: AsyncSession,
        delete_event: DeleteTeachScheduleEventModel,
        current_user: str | None = None,
    ):
        """
        删除排课事件service
        """
        event_ids = [int(id_str) for id_str in delete_event.event_ids.split(',') if id_str.strip()]
        if not event_ids:
            raise ServiceException(message='请选择要删除的课次')
        events = await TeachScheduleEventDao.get_raw_schedule_events_by_ids(query_db, event_ids)
        affected_class_ids = {event.class_id for event in events if event.class_id}
        try:
            await TeachScheduleEventDao.delete_teach_schedule_event(query_db, event_ids, current_user)
            for event_id in event_ids:
                await TeachScheduleAttendanceDao.delete_attendances_by_event(query_db, event_id)
            for class_id in affected_class_ids:
                await cls.refresh_class_total_lessons(query_db, class_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_calendar_events_services(
        cls,
        request,
        query_db: AsyncSession,
        query: CalendarQueryModel,
    ):
        """
        获取日历事件service
        """
        page_query = TeachScheduleEventPageQueryModel(
            page_num=1,
            page_size=1000,
            teacher_id=query.teacher_id,
            class_id=query.class_id,
            course_id=query.course_id,
            classroom=query.classroom,
            start_time=query.start,
            end_time=query.end,
        )
        events = await TeachScheduleEventDao.get_teach_schedule_event_list(
            query_db, page_query, data_scope_sql='', is_page=False
        )

        calendar_events = []
        for row in events:
            event = cls.format_event_row(row)
            start_time = event.get('startTime')
            end_time = event.get('endTime')
            calendar_events.append(
                {
                    'id': event.get('id'),
                    'title': f"{event.get('className') or ''} {event.get('courseName') or ''}".strip(),
                    'start': start_time.isoformat() if start_time else None,
                    'end': end_time.isoformat() if end_time else None,
                    'resourceId': event.get('teacherId'),
                    'extendedProps': event,
                }
            )

        return calendar_events
