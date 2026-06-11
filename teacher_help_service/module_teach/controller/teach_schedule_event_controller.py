from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.service.login_service import LoginService, CurrentUserModel
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.aspect.data_scope import GetDataScope
from module_teach.service.teach_schedule_event_service import TeachScheduleEventService
from module_teach.entity.vo.teach_schedule_event_vo import (
    TeachScheduleEventPageQueryModel,
    AddTeachScheduleEventModel,
    EditTeachScheduleEventModel,
    DeleteTeachScheduleEventModel,
    TeachScheduleEventDetailModel,
    CalendarQueryModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger


teachScheduleEventController = APIRouter(prefix='/teach/schedule/event', dependencies=[Depends(LoginService.get_current_user)])


@teachScheduleEventController.get(
    '/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:list'))]
)
async def get_teach_schedule_event_list(
    request: Request,
    event_page_query: TeachScheduleEventPageQueryModel = Depends(TeachScheduleEventPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('TeachScheduleEvent'))
):
    """
    获取排课事件分页列表

    Args:
        request: 请求对象
        event_page_query: 分页查询参数
        query_db: 数据库会话
        current_user: 当前用户
        data_scope_sql: 数据权限SQL

    Returns:
        排课事件分页列表响应
    """
    event_page_query_result = await TeachScheduleEventService.get_teach_schedule_event_list_services(
        request, query_db, event_page_query, data_scope_sql
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=event_page_query_result)


@teachScheduleEventController.get(
    '/{event_id}',
    response_model=TeachScheduleEventDetailModel,
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:query'))]
)
async def get_teach_schedule_event_detail(
    request: Request,
    event_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取排课事件详情

    Args:
        request: 请求对象
        event_id: 事件ID
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        排课事件详情响应
    """
    event_detail = await TeachScheduleEventService.get_teach_schedule_event_detail_services(
        request, query_db, event_id
    )

    if event_detail.id:
        logger.info('获取成功')
        return ResponseUtil.success(data=event_detail.model_dump(by_alias=True))
    else:
        logger.warning('排课事件不存在')
        return ResponseUtil.failure(msg='排课事件不存在')


@teachScheduleEventController.post(
    '',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:add'))]
)
@ValidateFields(validate_model='add_event')
@Log(title='排课管理', business_type=BusinessType.INSERT)
async def add_teach_schedule_event(
    request: Request,
    add_event: AddTeachScheduleEventModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    新增排课事件

    Args:
        request: 请求对象
        add_event: 新增事件模型
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        新增结果
    """
    add_event.validate_fields()
    result = await TeachScheduleEventService.add_teach_schedule_event_services(
        query_db, add_event, current_user.user.user_name
    )
    logger.info(result.message)

    if result.is_success:
        return ResponseUtil.success(msg=result.message)
    else:
        return ResponseUtil.failure(msg=result.message)


@teachScheduleEventController.put(
    '',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:edit'))]
)
@ValidateFields(validate_model='edit_event')
@Log(title='排课管理', business_type=BusinessType.UPDATE)
async def edit_teach_schedule_event(
    request: Request,
    edit_event: EditTeachScheduleEventModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    编辑排课事件

    Args:
        request: 请求对象
        edit_event: 编辑事件模型
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        编辑结果
    """
    edit_event.validate_fields()
    result = await TeachScheduleEventService.edit_teach_schedule_event_services(
        query_db, edit_event, current_user.user.user_name
    )
    logger.info(result.message)

    if result.is_success:
        return ResponseUtil.success(msg=result.message)
    else:
        return ResponseUtil.failure(msg=result.message)


@teachScheduleEventController.delete(
    '/{event_ids}',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:remove'))]
)
@Log(title='排课管理', business_type=BusinessType.DELETE)
async def delete_teach_schedule_event(
    request: Request,
    event_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    删除排课事件

    Args:
        request: 请求对象
        event_ids: 事件ID列表（逗号分隔）
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        删除结果
    """
    delete_event = DeleteTeachScheduleEventModel(event_ids=event_ids)
    delete_event.validate_fields()
    result = await TeachScheduleEventService.delete_teach_schedule_event_services(
        query_db, delete_event
    )
    logger.info(result.message)

    if result.is_success:
        return ResponseUtil.success(msg=result.message)
    else:
        return ResponseUtil.failure(msg=result.message)


@teachScheduleEventController.get(
    '/calendar/events',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:list'))]
)
async def get_calendar_events(
    request: Request,
    teacher_id: int = None,
    start: str = None,
    end: str = None,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取日历事件（用于FullCalendar）

    Args:
        request: 请求对象
        teacher_id: 教师ID（可选）
        start: 开始时间（ISO8601格式）
        end: 结束时间（ISO8601格式）
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        日历事件列表
    """
    from datetime import datetime
    calendar_query = CalendarQueryModel(
        teacher_id=teacher_id,
        start=datetime.fromisoformat(start.replace('Z', '+00:00')),
        end=datetime.fromisoformat(end.replace('Z', '+00:00'))
    )
    calendar_query.validate_fields()

    events = await TeachScheduleEventService.get_calendar_events_services(
        request, query_db, calendar_query
    )
    logger.info('获取成功')

    return ResponseUtil.success(data=events)

