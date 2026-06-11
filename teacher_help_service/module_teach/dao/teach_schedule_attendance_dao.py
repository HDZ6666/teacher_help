from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.vo.teach_schedule_attendance_vo import TeachScheduleAttendancePageQueryModel
from utils.page_util import PageUtil


class TeachScheduleAttendanceDao:
    """
    考勤管理模块数据库操作层
    """

    @classmethod
    async def get_teach_schedule_attendance_list(
        cls,
        db: AsyncSession,
        query_object: TeachScheduleAttendancePageQueryModel,
        is_page: bool = False
    ):
        """
        获取考勤分页列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 考勤列表信息对象
        """
        query = select(TeachScheduleAttendance, TeachStudent).join(
            TeachStudent,
            TeachScheduleAttendance.student_id == TeachStudent.id
        ).where(
            and_(
                TeachScheduleAttendance.del_flag == '0',
                TeachStudent.del_flag == '0'
            )
        )
        if query_object.event_id:
            query = query.where(TeachScheduleAttendance.event_id == query_object.event_id)
        if query_object.student_id:
            query = query.where(TeachScheduleAttendance.student_id == query_object.student_id)
        if query_object.status is not None:
            query = query.where(TeachScheduleAttendance.status == query_object.status)
        query = query.order_by(TeachScheduleAttendance.student_id)
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_attendance_by_event_and_student(
        cls,
        db: AsyncSession,
        event_id: int,
        student_id: int
    ):
        """
        根据事件ID和学生ID获取考勤记录

        :param db: orm对象
        :param event_id: 事件ID
        :param student_id: 学生ID
        :return: 考勤记录信息对象
        """
        query = select(TeachScheduleAttendance).where(
            and_(
                TeachScheduleAttendance.event_id == event_id,
                TeachScheduleAttendance.student_id == student_id,
                TeachScheduleAttendance.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def add_attendance(cls, db: AsyncSession, attendance: TeachScheduleAttendance):
        """
        新增考勤记录

        :param db: orm对象
        :param attendance: 考勤对象
        :return: 新增的考勤ID
        """
        db.add(attendance)
        await db.flush()
        return attendance.id

    @classmethod
    async def batch_add_attendances(cls, db: AsyncSession, attendances: List[TeachScheduleAttendance]):
        """
        批量新增考勤记录

        :param db: orm对象
        :param attendances: 考勤对象列表
        """
        db.add_all(attendances)
        await db.flush()

    @classmethod
    async def update_attendance(cls, db: AsyncSession, attendance: TeachScheduleAttendance):
        """
        更新考勤记录

        :param db: orm对象
        :param attendance: 考勤对象
        """
        await db.merge(attendance)

    @classmethod
    async def get_attendance_stat_by_event(cls, db: AsyncSession, event_id: int):
        """
        获取事件的考勤统计

        :param db: orm对象
        :param event_id: 事件ID
        :return: 统计字典
        """
        query = select(
            func.count(TeachScheduleAttendance.id).label('total'),
            func.sum(func.if_(TeachScheduleAttendance.is_countable == 1, 1, 0)).label('planned'),
            func.sum(func.if_(TeachScheduleAttendance.status == 1, 1, 0)).label('present'),
            func.sum(func.if_(TeachScheduleAttendance.status == 2, 1, 0)).label('late'),
            func.sum(func.if_(TeachScheduleAttendance.status == 3, 1, 0)).label('excused'),
            func.sum(func.if_(TeachScheduleAttendance.status == 4, 1, 0)).label('absent'),
            func.sum(func.if_(TeachScheduleAttendance.status == 0, 1, 0)).label('not_arrived')
        ).where(
            and_(
                TeachScheduleAttendance.event_id == event_id,
                TeachScheduleAttendance.del_flag == '0'
            )
        )
        result = await db.execute(query)
        row = result.first()
        if row:
            return {
                'total': row.total or 0,
                'planned': row.planned or 0,
                'present': row.present or 0,
                'late': row.late or 0,
                'excused': row.excused or 0,
                'absent': row.absent or 0,
                'not_arrived': row.not_arrived or 0
            }
        return {
            'total': 0,
            'planned': 0,
            'present': 0,
            'late': 0,
            'excused': 0,
            'absent': 0,
            'not_arrived': 0
        }

    @classmethod
    async def get_attendances_by_event(cls, db: AsyncSession, event_id: int):
        """
        获取事件的所有考勤记录

        :param db: orm对象
        :param event_id: 事件ID
        :return: 考勤记录列表
        """
        query = select(TeachScheduleAttendance).where(
            and_(
                TeachScheduleAttendance.event_id == event_id,
                TeachScheduleAttendance.del_flag == '0'
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_attendances_with_students_by_event(
        cls,
        db: AsyncSession,
        event_id: int
    ):
        """
        获取事件的所有考勤记录

        :param db: orm对象
        :param event_id: 事件ID
        :return: 考勤记录列表信息对象
        """
        query = select(TeachScheduleAttendance, TeachStudent).join(
            TeachStudent,
            TeachScheduleAttendance.student_id == TeachStudent.id
        ).where(
            and_(
                TeachScheduleAttendance.event_id == event_id,
                TeachScheduleAttendance.del_flag == '0',
                TeachStudent.del_flag == '0'
            )
        ).order_by(TeachScheduleAttendance.student_id)
        result = await db.execute(query)
        return result.all()

    @classmethod
    async def delete_attendances_by_event(cls, db: AsyncSession, event_id: int):
        """
        删除事件的所有考勤记录数据库操作

        :param db: orm对象
        :param event_id: 事件ID
        """
        attendances = await cls.get_attendances_by_event(db, event_id)
        for attendance in attendances:
            attendance.del_flag = '2'
            attendance.update_time = datetime.now()

