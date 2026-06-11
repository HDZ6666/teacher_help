from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.dao.teach_schedule_event_dao import TeachScheduleEventDao
from module_teach.dao.teach_schedule_attendance_dao import TeachScheduleAttendanceDao
from module_teach.dao.teach_teacher_dao import TeachTeacherDao
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.vo.teach_schedule_event_vo import (
    TeachScheduleEventPageQueryModel,
    AddTeachScheduleEventModel,
    EditTeachScheduleEventModel,
    DeleteTeachScheduleEventModel,
    TeachScheduleEventDetailModel,
    CalendarQueryModel
)
from utils.common_util import CamelCaseUtil
from module_admin.entity.vo.common_vo import CrudResponseModel
from exceptions.exception import ServiceException


class TeachScheduleEventService:
    """
    排课事件管理模块服务层
    """

    @classmethod
    async def get_teach_schedule_event_list_services(
        cls,
        request,
        query_db: AsyncSession,
        query_object: TeachScheduleEventPageQueryModel,
        data_scope_sql: str,
        is_page: bool = False
    ):
        """
        获取排课事件列表信息service

        :param request: 请求对象
        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 排课事件列表信息对象
        """
        event_list_result = await TeachScheduleEventDao.get_teach_schedule_event_list(
            query_db, query_object, data_scope_sql, is_page
        )

        # 处理返回数据 - PageUtil已经转为字典，直接使用字典解包
        if is_page:
            # 分页结果 - rows 已经是字典列表
            rows = [{**row[0], 'teacherName': row[1].get('teacherName') if isinstance(row[1], dict) else ''} for row in event_list_result.rows]

            from utils.page_util import PageResponseModel
            return PageResponseModel(
                **{
                    **event_list_result.model_dump(by_alias=True),
                    'rows': rows
                }
            )
        else:
            # 非分页结果 - 已经是字典列表
            result_list = [{**row[0], 'teacherName': row[1].get('teacherName') if isinstance(row[1], dict) else ''} for row in event_list_result]
            return result_list

    @classmethod
    async def get_teach_schedule_event_detail_services(
        cls,
        request,
        query_db: AsyncSession,
        event_id: int
    ):
        """
        获取排课事件详情service

        :param request: 请求对象
        :param query_db: orm对象
        :param event_id: 事件ID
        :return: 排课事件详情信息对象
        """
        event_result = await TeachScheduleEventDao.get_teach_schedule_event_by_id(query_db, event_id)
        if not event_result:
            return TeachScheduleEventDetailModel()
        event_obj, teacher_obj = event_result
        detail = TeachScheduleEventDetailModel(
            id=event_obj.id,
            teacher_id=event_obj.teacher_id,
            teacher_name=teacher_obj.teacher_name,
            subject_code=event_obj.subject_code,
            start_time=event_obj.start_time,
            end_time=event_obj.end_time,
            event_date=event_obj.event_date,
            status=event_obj.status,
            roster_frozen_at=event_obj.roster_frozen_at,
            cached_planned=event_obj.cached_planned,
            cached_present=event_obj.cached_present,
            cached_late=event_obj.cached_late,
            cached_excused=event_obj.cached_excused,
            cached_absent=event_obj.cached_absent,
            cached_rate=float(event_obj.cached_rate) if event_obj.cached_rate else None,
            create_time=event_obj.create_time,
            remark=event_obj.remark
        )
        attendance_with_students = await TeachScheduleAttendanceDao.get_attendances_with_students_by_event(
            query_db, event_id
        )
        students = []
        for att, student in attendance_with_students:
            students.append({
                'student_id': student.id,
                'student_name': student.student_name,
                'status': att.status,
                'check_in_time': att.check_in_time
            })
        detail.students = students

        return detail

    @classmethod
    async def add_teach_schedule_event_services(
        cls,
        query_db: AsyncSession,
        add_event: AddTeachScheduleEventModel,
        current_user: str
    ):
        """
        新增排课事件service

        :param query_db: orm对象
        :param add_event: 新增排课事件对象
        :param current_user: 当前用户名
        :return: 新增排课事件校验结果
        """
        teacher = await TeachTeacherDao.get_teach_teacher_by_id(query_db, add_event.teacher_id)
        if not teacher:
            raise ServiceException(message='教师不存在')
        has_conflict = await TeachScheduleEventDao.check_time_conflict(
            query_db, add_event.teacher_id, add_event.start_time, add_event.end_time
        )
        if has_conflict:
            raise ServiceException(message='该时间段与教师的其他课程冲突')
        event = TeachScheduleEvent(
            teacher_id=add_event.teacher_id,
            subject_code=add_event.subject_code,
            start_time=add_event.start_time,
            end_time=add_event.end_time,
            event_date=add_event.start_time.date(),
            status='0',
            cached_planned=len(add_event.student_ids),
            create_by=current_user,
            update_by=current_user,
            remark=add_event.remark
        )
        event_id = await TeachScheduleEventDao.add_teach_schedule_event(query_db, event)
        attendances = []
        for student_id in add_event.student_ids:
            attendance = TeachScheduleAttendance(
                event_id=event_id,
                student_id=student_id,
                status=0,
                is_countable=1,
                create_by=current_user,
                update_by=current_user
            )
            attendances.append(attendance)
        if attendances:
            await TeachScheduleAttendanceDao.batch_add_attendances(query_db, attendances)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='排课成功')

    @classmethod
    async def edit_teach_schedule_event_services(
        cls,
        query_db: AsyncSession,
        edit_event: EditTeachScheduleEventModel,
        current_user: str
    ):
        """
        编辑排课事件service

        :param query_db: orm对象
        :param edit_event: 编辑排课事件对象
        :param current_user: 当前用户名
        :return: 编辑排课事件校验结果
        """
        event = await TeachScheduleEventDao.get_teach_schedule_event_by_id(query_db, edit_event.id)
        if not event:
            raise ServiceException(message='排课事件不存在')
        if edit_event.start_time or edit_event.end_time:
            start_time = edit_event.start_time or event.start_time
            end_time = edit_event.end_time or event.end_time
            teacher_id = edit_event.teacher_id or event.teacher_id
            has_conflict = await TeachScheduleEventDao.check_time_conflict(
                query_db, teacher_id, start_time, end_time, exclude_event_id=edit_event.id
            )
            if has_conflict:
                raise ServiceException(message='该时间段与教师的其他课程冲突')
        if edit_event.teacher_id is not None:
            event.teacher_id = edit_event.teacher_id
        if edit_event.subject_code is not None:
            event.subject_code = edit_event.subject_code
        if edit_event.start_time is not None:
            event.start_time = edit_event.start_time
            event.event_date = edit_event.start_time.date()
        if edit_event.end_time is not None:
            event.end_time = edit_event.end_time
        if edit_event.status is not None:
            event.status = edit_event.status
        if edit_event.remark is not None:
            event.remark = edit_event.remark
        event.update_by = current_user
        event.update_time = datetime.now()
        await TeachScheduleEventDao.edit_teach_schedule_event(query_db, event)
        if edit_event.student_ids is not None:
            await TeachScheduleAttendanceDao.delete_attendances_by_event(query_db, edit_event.id)
            attendances = []
            for student_id in edit_event.student_ids:
                attendance = TeachScheduleAttendance(
                    event_id=edit_event.id,
                    student_id=student_id,
                    status=0,
                    is_countable=1,
                    create_by=current_user,
                    update_by=current_user
                )
                attendances.append(attendance)
            if attendances:
                await TeachScheduleAttendanceDao.batch_add_attendances(query_db, attendances)
            event.cached_planned = len(edit_event.student_ids)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_teach_schedule_event_services(
        cls,
        query_db: AsyncSession,
        delete_event: DeleteTeachScheduleEventModel
    ):
        """
        删除排课事件service

        :param query_db: orm对象
        :param delete_event: 删除排课事件对象
        :return: 删除排课事件校验结果
        """
        event_ids = [int(id_str) for id_str in delete_event.event_ids.split(',')]
        await TeachScheduleEventDao.delete_teach_schedule_event(query_db, event_ids)
        for event_id in event_ids:
            await TeachScheduleAttendanceDao.delete_attendances_by_event(query_db, event_id)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def get_calendar_events_services(
        cls,
        request,
        query_db: AsyncSession,
        query: CalendarQueryModel
    ):
        """
        获取日历事件service

        :param request: 请求对象
        :param query_db: orm对象
        :param query: 日历查询参数对象
        :return: 日历事件列表
        """
        page_query = TeachScheduleEventPageQueryModel(
            page_num=1,
            page_size=1000,
            teacher_id=query.teacher_id,
            start_time=query.start,
            end_time=query.end
        )
        events = await TeachScheduleEventDao.get_teach_schedule_event_list(
            query_db, page_query, is_page=False
        )

        # 转换为FullCalendar格式 - events 已经是字典列表
        calendar_events = []
        for row in events:
            event = row[0] if isinstance(row[0], dict) else {}
            teacher = row[1] if isinstance(row[1], dict) else {}
            
            calendar_events.append({
                'id': event.get('id'),
                'title': f"{event.get('subjectCode', '')} - {teacher.get('teacherName', '')}",
                'start': event.get('startTime').isoformat() if event.get('startTime') else None,
                'end': event.get('endTime').isoformat() if event.get('endTime') else None,
                'resourceId': event.get('teacherId'),
                'extendedProps': {
                    'teacherId': event.get('teacherId'),
                    'teacherName': teacher.get('teacherName'),
                    'subjectCode': event.get('subjectCode'),
                    'status': event.get('status'),
                    'planned': event.get('cachedPlanned') or 0,
                    'present': event.get('cachedPresent') or 0,
                    'late': event.get('cachedLate') or 0,
                    'rate': float(event.get('cachedRate')) if event.get('cachedRate') else 0
                }
            })

        return calendar_events

