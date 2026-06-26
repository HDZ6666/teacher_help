from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_leave_dao import TeachLeaveDao
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

    @classmethod
    async def approve_leave_services(
        cls, query_db: AsyncSession, page_object: ApproveTeachLeaveModel, current_user_name: str
    ):
        leave = await TeachLeaveDao.get_leave_by_id(query_db, page_object.id)
        if not leave:
            raise ServiceException(message='请假申请不存在')
        if leave.leave_status != 1:
            raise ServiceException(message='该请假申请已审批，不能重复审批')
        if page_object.leave_status not in [2, 3]:
            raise ServiceException(message='审批结果不正确')
        try:
            leave.leave_status = page_object.leave_status
            leave.approver_id = None
            leave.approver_name = current_user_name
            leave.approve_time = datetime.now()
            leave.approve_remark = page_object.approve_remark
            leave.update_by = current_user_name
            await TeachLeaveDao.edit_leave(query_db, leave)
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
            await TeachLeaveDao.delete_leave(query_db, leave_ids, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='撤销成功')
        except Exception as e:
            await query_db.rollback()
            raise e
