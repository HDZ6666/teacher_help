from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.service.login_service import LoginService, CurrentUserModel
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.aspect.data_scope import GetDataScope
from module_teach.service.teach_parent_service import TeachParentService
from module_teach.entity.vo.teach_parent_vo import (
    TeachParentPageQueryModel,
    AddTeachParentModel,
    EditTeachParentModel,
    DeleteTeachParentModel,
    TeachParentResponseModel,
    TeachParentDetailModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.common_util import bytes2file_response
from utils.log_util import logger


teachParentController = APIRouter(prefix='/teach/parent', dependencies=[Depends(LoginService.get_current_user)])


@teachParentController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:parent:list'))])
async def get_teach_parent_list(
    request: Request,
    parent_page_query: TeachParentPageQueryModel = Depends(TeachParentPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('TeachParent'))
):
    parent_page_query_result = await TeachParentService.get_teach_parent_list_services(
        query_db, parent_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=parent_page_query_result)


@teachParentController.get('/{parent_id}', response_model=TeachParentDetailModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:parent:query'))])
async def get_teach_parent_detail(
    request: Request,
    parent_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    parent_detail = await TeachParentService.get_teach_parent_detail_services(query_db, parent_id)

    if parent_detail.id:
        logger.info('获取成功')
        return ResponseUtil.success(data=parent_detail.model_dump(by_alias=True))
    else:
        logger.warning('家长不存在')
        return ResponseUtil.failure(msg='家长不存在')


@teachParentController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:parent:add'))])
@ValidateFields(validate_model='add_parent')
@Log(title='家长管理', business_type=BusinessType.INSERT)
async def add_teach_parent(
    request: Request,
    add_parent: AddTeachParentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    add_result = await TeachParentService.add_teach_parent_services(query_db, add_parent, current_user.user.user_name)
    logger.info(add_result.message)

    return ResponseUtil.success(msg=add_result.message)


@teachParentController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:parent:edit'))])
@ValidateFields(validate_model='edit_parent')
@Log(title='家长管理', business_type=BusinessType.UPDATE)
async def edit_teach_parent(
    request: Request,
    edit_parent: EditTeachParentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    edit_result = await TeachParentService.edit_teach_parent_services(query_db, edit_parent, current_user.user.user_name)
    logger.info(edit_result.message)

    return ResponseUtil.success(msg=edit_result.message)


@teachParentController.delete('/{parent_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:parent:remove'))])
@Log(title='家长管理', business_type=BusinessType.DELETE)
async def delete_teach_parent(
    request: Request,
    parent_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    delete_parent = DeleteTeachParentModel(ids=parent_ids)
    delete_result = await TeachParentService.delete_teach_parent_services(query_db, delete_parent, current_user.user.user_name)
    logger.info(delete_result.message)

    return ResponseUtil.success(msg=delete_result.message)


@teachParentController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:parent:export'))])
@Log(title='家长管理', business_type=BusinessType.EXPORT)
async def export_teach_parent_list(
    request: Request,
    parent_page_query: TeachParentPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('TeachParent'))
):
    parent_query_result = await TeachParentService.get_teach_parent_list_services(
        query_db, parent_page_query, data_scope_sql, is_page=False
    )
    parent_export_result = await TeachParentService.export_teach_parent_list_services(parent_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(parent_export_result))
