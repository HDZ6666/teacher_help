from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_leave_vo import (
    AddTeachLeaveModel,
    ApproveTeachLeaveModel,
    DeleteTeachLeaveModel,
    TeachLeavePageQueryModel,
)
from module_teach.service.teach_leave_service import TeachLeaveService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachLeaveController = APIRouter(prefix='/teach/leave', dependencies=[Depends(LoginService.get_current_user)])


@teachLeaveController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:leave:list'))]
)
async def get_teach_leave_list(
    request: Request,
    leave_page_query: TeachLeavePageQueryModel = Depends(TeachLeavePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachLeaveService.get_leave_list_services(query_db, leave_page_query)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachLeaveController.get('/{leave_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:leave:query'))])
async def get_teach_leave_detail(request: Request, leave_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachLeaveService.get_leave_detail_services(query_db, leave_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachLeaveController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:leave:add'))])
@Log(title='请假申请', business_type=BusinessType.INSERT)
async def add_teach_leave(
    request: Request,
    add_leave: AddTeachLeaveModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLeaveService.add_leave_services(query_db, add_leave, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachLeaveController.put('/approve', dependencies=[Depends(CheckUserInterfaceAuth('teach:leave:edit'))])
@Log(title='请假审批', business_type=BusinessType.UPDATE)
async def approve_teach_leave(
    request: Request,
    approve_leave: ApproveTeachLeaveModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLeaveService.approve_leave_services(query_db, approve_leave, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachLeaveController.delete('/{leave_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:leave:remove'))])
@Log(title='请假申请', business_type=BusinessType.DELETE)
async def delete_teach_leave(
    request: Request,
    leave_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_leave = DeleteTeachLeaveModel(leave_ids=leave_ids)
    result = await TeachLeaveService.delete_leave_services(query_db, delete_leave, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
