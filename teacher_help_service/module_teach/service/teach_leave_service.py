from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_leave_dao import TeachLeaveDao
from module_teach.dao.teach_schedule_attendance_dao import TeachScheduleAttendanceDao
from module_teach.dao.teach_schedule_event_dao import TeachScheduleEventDao
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.entity.do.teach_leave_do import TeachLeaveApplication
from module_teach.entity.vo.teach_leave_vo import (
    AddTeachLeaveModel,
    ApproveTeachLeaveModel,
    DeleteTeachLeaveModel,
    TeachLeavePageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachLeaveService:
    """
    请假申请模块服务层
    """

    LEAVE_TYPE_LABELS = {
        1: '事假',
        2: '病假',
        3: '其他',
    }
    LEAVE_STATUS_LABELS = {
        1: '待审批',
        2: '已通过',
        3: '已拒绝',
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
    def make_leave_no(cls):
        return f'LV{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def to_int(cls, value, default=0):
        if value in [None, '']:
            return default
        return int(value)

    @classmethod
    def format_leave_row(cls, leave: TeachLeaveApplication):
        row = CamelCaseUtil.transform_result(leave)
        row['leaveTypeName'] = cls.LEAVE_TYPE_LABELS.get(leave.leave_type, '-')
        row['leaveStatusName'] = cls.LEAVE_STATUS_LABELS.get(leave.leave_status, '-')
        row['isDeductName'] = '是' if leave.is_deduct == 1 else '否'
        return row

    @classmethod
    async def get_leave_list_services(cls, query_db: AsyncSession, query_object: TeachLeavePageQueryModel):
        rows, total = await TeachLeaveDao.get_leave_list(query_db, query_object)
        return cls.make_page(
            [cls.format_leave_row(row) for row in rows],
            total,
            query_object.page_num,
            query_object.page_size,
        )

    @classmethod
    async def get_leave_detail_services(cls, query_db: AsyncSession, leave_id: int):
        leave = await TeachLeaveDao.get_leave_by_id(query_db, leave_id)
        if not leave:
            raise ServiceException(message='请假申请不存在')
        return cls.format_leave_row(leave)

    @classmethod
    async def add_leave_services(
        cls, query_db: AsyncSession, page_object: AddTeachLeaveModel, current_user_name: str
    ):
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, page_object.student_id)
        if not student_result:
            raise ServiceException(message='请假学员不存在')
        student = student_result[0]

        class_id = page_object.class_id
        class_name = None
        course_id = page_object.course_id
        course_name = None
        event_id = page_object.event_id
        leave_date = page_object.leave_date

        # 按课次请假：以课次快照补全班级/课程/日期
        if event_id:
            event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, event_id)
            if not event:
                raise ServiceException(message='请假课次不存在')
            class_id = class_id or event.class_id
            class_name = event.class_name
            course_id = course_id or event.course_id
            course_name = event.course_name
            leave_date = leave_date or event.event_date

        if class_id:
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
            if not class_obj:
                raise ServiceException(message='请假班级不存在')
            class_name = class_name or class_obj.class_name
            course_id = course_id or class_obj.course_id
            course_name = course_name or class_obj.course_name

        if course_id and not course_name:
            course = await TeachCourseDao.get_teach_course_by_id(query_db, course_id)
            if not course:
                raise ServiceException(message='请假课程不存在')
            course_name = course.course_name

        if not leave_date:
            raise ServiceException(message='请选择请假课次或请假日期')

        try:
            leave_obj = TeachLeaveApplication(
                leave_no=cls.make_leave_no(),
                student_id=student.id,
                student_name=student.student_name,
                class_id=class_id,
                class_name=class_name,
                course_id=course_id,
                course_name=course_name,
                event_id=event_id,
                leave_type=cls.to_int(page_object.leave_type, 1),
                leave_date=leave_date,
                leave_reason=page_object.leave_reason,
                leave_image=page_object.leave_image,
                is_deduct=cls.to_int(page_object.is_deduct, 0),
                leave_status=1,
                applicant_id=None,
                applicant_name=current_user_name,
                apply_time=datetime.now(),
                create_by=current_user_name,
                create_time=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now(),
                remark=page_object.remark,
            )
            leave_obj = await TeachLeaveDao.add_leave(query_db, leave_obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='提交成功', result={'id': leave_obj.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    # 课表考勤表(teach_schedule_attendances) status：0未到 3请假
    SCHEDULE_STATUS_PENDING = 0
    SCHEDULE_STATUS_LEAVE = 3
    # 班级点名明细(teach_class_attendance_detail) status：3请假 4未到
    CLASS_STATUS_LEAVE = 3
    CLASS_STATUS_ABSENT = 4

    @classmethod
    async def get_leave_target_events(cls, query_db: AsyncSession, leave: TeachLeaveApplication):
        """
        请假影响的排课课次：按课次请假取该课次；按日期请假且指定了班级时取该班级当天未取消的课次
        仅按日期、未指定班级的请假不在审批时联动，由点名时按日期匹配
        """
        if leave.event_id:
            event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, leave.event_id)
            return [event] if event and event.status != '3' else []
        if leave.class_id and leave.leave_date:
            return list(await TeachLeaveDao.get_class_events_by_date(query_db, leave.class_id, leave.leave_date))
        return []

    @classmethod
    async def sync_leave_to_attendance(
        cls, query_db: AsyncSession, leave: TeachLeaveApplication, approved: bool, current_user_name: str
    ):
        """
        请假与考勤联动（在调用方事务中执行，不提交）：
        - 审批通过、课次未点名：课表考勤名单中该学员标记为“请假”，点名页默认带出请假状态
        - 审批通过、课次已点名：仅把“未到”更正为“请假”并同步统计；已到课/迟到的保持不变（学员实际来了）；
          “未到”本来就不扣课，因此不涉及退课时
        - 撤销已通过的请假、课次未点名：课表考勤中由请假带出的“请假”状态恢复为“未到”
        - 撤销时课次已点名：保留点名历史，不做回滚
        """
        affected_events = 0
        for event in await cls.get_leave_target_events(query_db, leave):
            if event.class_id:
                # 与点名提交使用同一把班级行锁，避免审批与点名交叉
                await TeachClassDao.get_teach_class_by_id(query_db, event.class_id, for_update=True)
            attendance = await TeachClassDao.get_class_attendance_by_event_id(query_db, event.id, for_update=True)
            schedule_rows = await TeachScheduleAttendanceDao.get_attendances_by_event(query_db, event.id)
            schedule_row = next((row for row in schedule_rows if row.student_id == leave.student_id), None)
            if attendance is None:
                if schedule_row is None:
                    continue
                if approved:
                    schedule_row.status = cls.SCHEDULE_STATUS_LEAVE
                    schedule_row.notes = f'请假：{leave.leave_no}'
                elif schedule_row.status == cls.SCHEDULE_STATUS_LEAVE and not schedule_row.check_in_time:
                    schedule_row.status = cls.SCHEDULE_STATUS_PENDING
                    schedule_row.notes = None
                else:
                    continue
                schedule_row.update_by = current_user_name
                schedule_row.update_time = datetime.now()
                affected_events += 1
                continue
            if not approved:
                continue
            detail = await TeachLeaveDao.get_attendance_detail_for_update(query_db, attendance.id, leave.student_id)
            if detail is None or detail.status != cls.CLASS_STATUS_ABSENT:
                continue
            detail.status = cls.CLASS_STATUS_LEAVE
            detail.remark = f'请假：{leave.leave_no}'
            detail.update_by = current_user_name
            detail.update_time = datetime.now()
            attendance.absent_count = max((attendance.absent_count or 0) - 1, 0)
            attendance.leave_count = (attendance.leave_count or 0) + 1
            attendance.update_by = current_user_name
            attendance.update_time = datetime.now()
            if schedule_row is not None:
                schedule_row.status = cls.SCHEDULE_STATUS_LEAVE
                schedule_row.update_by = current_user_name
                schedule_row.update_time = datetime.now()
            event.cached_absent = max((event.cached_absent or 0) - 1, 0)
            event.cached_excused = (event.cached_excused or 0) + 1
            event.update_by = current_user_name
            event.update_time = datetime.now()
            affected_events += 1
        await query_db.flush()
        return affected_events

    @classmethod
    async def approve_leave_services(
        cls, query_db: AsyncSession, page_object: ApproveTeachLeaveModel, current_user_name: str
    ):
        if page_object.leave_status not in [2, 3]:
            raise ServiceException(message='审批结果不正确')
        try:
            leave = await TeachLeaveDao.get_leave_by_id(query_db, page_object.id, for_update=True)
            if not leave:
                raise ServiceException(message='请假申请不存在')
            if leave.leave_status != 1:
                raise ServiceException(message='该请假申请已审批，不能重复审批')
            leave.leave_status = page_object.leave_status
            leave.approver_id = None
            leave.approver_name = current_user_name
            leave.approve_time = datetime.now()
            leave.approve_remark = page_object.approve_remark
            leave.update_by = current_user_name
            await TeachLeaveDao.edit_leave(query_db, leave)
            if page_object.leave_status == 2:
                await cls.sync_leave_to_attendance(query_db, leave, True, current_user_name)
            await query_db.commit()
            message = '审批通过' if page_object.leave_status == 2 else '已拒绝'
            return CrudResponseModel(is_success=True, message=message)
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_leave_services(
        cls, query_db: AsyncSession, page_object: DeleteTeachLeaveModel, current_user_name: str
    ):
        leave_ids = [int(item) for item in page_object.leave_ids.split(',') if item.strip()]
        if not leave_ids:
            raise ServiceException(message='请选择要撤销的请假申请')
        try:
            for leave in await TeachLeaveDao.get_leaves_by_ids(query_db, leave_ids):
                if leave.leave_status == 2:
                    await cls.sync_leave_to_attendance(query_db, leave, False, current_user_name)
            await TeachLeaveDao.delete_leave(query_db, leave_ids, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='撤销成功')
        except Exception as e:
            await query_db.rollback()
            raise e
