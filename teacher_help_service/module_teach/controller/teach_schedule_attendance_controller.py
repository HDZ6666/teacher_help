from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.service.login_service import LoginService, CurrentUserModel
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_teach.service.teach_schedule_attendance_service import TeachScheduleAttendanceService
from module_teach.entity.vo.teach_schedule_attendance_vo import (
    TeachScheduleAttendancePageQueryModel,
    CheckInModel,
    ManualAttendanceModel,
    AttendanceStatModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger


teachScheduleAttendanceController = APIRouter(prefix='/teach/schedule/attendance', dependencies=[Depends(LoginService.get_current_user)])


@teachScheduleAttendanceController.get(
    '/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:attendance:list'))]
)
async def get_teach_schedule_attendance_list(
    request: Request,
    attendance_page_query: TeachScheduleAttendancePageQueryModel = Depends(TeachScheduleAttendancePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取考勤分页列表

    Args:
        request: 请求对象
        attendance_page_query: 分页查询参数
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        考勤分页列表响应
    """
    attendance_page_query_result = await TeachScheduleAttendanceService.get_teach_schedule_attendance_list_services(
        request, query_db, attendance_page_query
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=attendance_page_query_result)


@teachScheduleAttendanceController.post(
    '/checkin',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:attendance:checkin'))]
)
@ValidateFields(validate_model='check_in')
@Log(title='考勤管理', business_type=BusinessType.INSERT)
async def check_in(
    request: Request,
    check_in: CheckInModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    签到

    Args:
        request: 请求对象
        check_in: 签到模型
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        签到结果
    """
    check_in.validate_fields()
    result = await TeachScheduleAttendanceService.check_in_services(
        query_db, check_in, current_user.user.user_name
    )
    logger.info(result.message)

    if result.is_success:
        return ResponseUtil.success(msg=result.message)
    else:
        return ResponseUtil.failure(msg=result.message)


@teachScheduleAttendanceController.post(
    '/manual',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:attendance:manual'))]
)
@ValidateFields(validate_model='manual')
@Log(title='考勤管理', business_type=BusinessType.UPDATE)
async def manual_attendance(
    request: Request,
    manual: ManualAttendanceModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    手动补录考勤

    Args:
        request: 请求对象
        manual: 手动考勤模型
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        补录结果
    """
    manual.validate_fields()
    result = await TeachScheduleAttendanceService.manual_attendance_services(
        query_db, manual, current_user.user.user_name, current_user.user.user_id
    )
    logger.info(result.message)

    if result.is_success:
        return ResponseUtil.success(msg=result.message)
    else:
        return ResponseUtil.failure(msg=result.message)


@teachScheduleAttendanceController.get(
    '/stat/{event_id}',
    response_model=AttendanceStatModel,
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:attendance:stat'))]
)
async def get_attendance_stat(
    request: Request,
    event_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取考勤统计

    Args:
        request: 请求对象
        event_id: 事件ID
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        考勤统计响应
    """
    stat = await TeachScheduleAttendanceService.get_attendance_stat_services(
        query_db, event_id
    )
    logger.info('获取成功')

    return ResponseUtil.success(data=stat.model_dump(by_alias=True))

