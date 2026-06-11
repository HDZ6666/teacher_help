from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.dao.teach_schedule_attendance_dao import TeachScheduleAttendanceDao
from module_teach.dao.teach_schedule_event_dao import TeachScheduleEventDao
from module_teach.entity.vo.teach_schedule_attendance_vo import (
    TeachScheduleAttendancePageQueryModel,
    CheckInModel,
    ManualAttendanceModel,
    AttendanceStatModel
)
from module_admin.entity.vo.common_vo import CrudResponseModel
from exceptions.exception import ServiceException


class TeachScheduleAttendanceService:
    """
    考勤管理模块服务层
    """

    @classmethod
    async def get_teach_schedule_attendance_list_services(
        cls,
        request,
        query_db: AsyncSession,
        query_object: TeachScheduleAttendancePageQueryModel,
        is_page: bool = False
    ):
        """
        获取考勤列表信息service

        :param request: 请求对象
        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 考勤列表信息对象
        """
        attendance_list_result = await TeachScheduleAttendanceDao.get_teach_schedule_attendance_list(
            query_db, query_object, is_page
        )

        # 处理返回数据 - PageUtil已经转为字典，直接使用字典解包
        if is_page:
            # 分页结果 - rows 已经是字典列表
            rows = [{**row[0], 'studentName': row[1].get('studentName') if isinstance(row[1], dict) else ''} for row in attendance_list_result.rows]

            from utils.page_util import PageResponseModel
            return PageResponseModel(
                **{
                    **attendance_list_result.model_dump(by_alias=True),
                    'rows': rows
                }
            )
        else:
            # 非分页结果 - 已经是字典列表
            result_list = [{**row[0], 'studentName': row[1].get('studentName') if isinstance(row[1], dict) else ''} for row in attendance_list_result]
            return result_list

    @classmethod
    async def check_in_services(
        cls,
        query_db: AsyncSession,
        check_in: CheckInModel,
        current_user: str
    ):
        """
        签到service

        :param query_db: orm对象
        :param check_in: 签到对象
        :param current_user: 当前用户名
        :return: 签到校验结果
        """
        attendance = await TeachScheduleAttendanceDao.get_attendance_by_event_and_student(
            query_db, check_in.event_id, check_in.student_id
        )
        if not attendance:
            raise ServiceException(message='该学生不在本节课的名单中')
        if attendance.status != 0:
            raise ServiceException(message='该学生已签到，无需重复签到')
        attendance.status = 1
        attendance.check_in_time = datetime.now()
        attendance.check_in_method = check_in.check_in_method
        attendance.notes = check_in.notes
        attendance.update_by = current_user
        attendance.update_time = datetime.now()
        await TeachScheduleAttendanceDao.update_attendance(query_db, attendance)
        await cls._update_event_cached_stats(query_db, check_in.event_id)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='签到成功')

    @classmethod
    async def manual_attendance_services(
        cls,
        query_db: AsyncSession,
        manual: ManualAttendanceModel,
        current_user: str,
        operator_id: int
    ):
        """
        手动补录考勤service

        :param query_db: orm对象
        :param manual: 手动考勤对象
        :param current_user: 当前用户名
        :param operator_id: 操作人ID
        :return: 手动补录考勤校验结果
        """
        attendance = await TeachScheduleAttendanceDao.get_attendance_by_event_and_student(
            query_db, manual.event_id, manual.student_id
        )
        if not attendance:
            raise ServiceException(message='该学生不在本节课的名单中')
        attendance.status = manual.status
        attendance.check_in_time = datetime.now()
        attendance.check_in_method = 'M'
        attendance.operator_id = operator_id
        attendance.notes = manual.notes
        attendance.update_by = current_user
        attendance.update_time = datetime.now()
        await TeachScheduleAttendanceDao.update_attendance(query_db, attendance)
        await cls._update_event_cached_stats(query_db, manual.event_id)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='考勤记录已更新')

    @classmethod
    async def get_attendance_stat_services(
        cls,
        query_db: AsyncSession,
        event_id: int
    ):
        """
        获取考勤统计service

        :param query_db: orm对象
        :param event_id: 事件ID
        :return: 考勤统计信息对象
        """
        stat = await TeachScheduleAttendanceDao.get_attendance_stat_by_event(query_db, event_id)

        # 计算出勤率
        planned = stat.get('planned', 0)
        present = stat.get('present', 0)
        late = stat.get('late', 0)

        if planned > 0:
            attendance_rate = round((present + late) / planned * 100, 2)
        else:
            attendance_rate = 0.0

        return AttendanceStatModel(
            event_id=event_id,
            total=stat.get('total', 0),
            planned=planned,
            present=present,
            late=late,
            excused=stat.get('excused', 0),
            absent=stat.get('absent', 0),
            not_arrived=stat.get('not_arrived', 0),
            attendance_rate=attendance_rate
        )

    @classmethod
    async def _update_event_cached_stats(cls, query_db: AsyncSession, event_id: int):
        """
        更新事件的缓存统计数据service

        :param query_db: orm对象
        :param event_id: 事件ID
        """
        stat = await TeachScheduleAttendanceDao.get_attendance_stat_by_event(query_db, event_id)
        planned = stat.get('planned', 0)
        present = stat.get('present', 0)
        late = stat.get('late', 0)
        excused = stat.get('excused', 0)
        absent = stat.get('absent', 0)
        if planned > 0:
            rate = round((present + late) / planned * 100, 2)
        else:
            rate = 0.0
        await TeachScheduleEventDao.update_cached_stats(
            query_db, event_id, planned, present, late, excused, absent, rate
        )

