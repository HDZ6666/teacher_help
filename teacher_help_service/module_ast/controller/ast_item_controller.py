from datetime import datetime
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.service.login_service import LoginService, CurrentUserModel
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.aspect.data_scope import GetDataScope
from module_ast.service.ast_item_service import AstItemService
from module_ast.entity.vo.ast_item_vo import (
    AstItemPageQueryModel,
    AddAstItemModel,
    EditAstItemModel,
    DeleteAstItemModel,
    AstItemDetailModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.log_util import logger


astItemController = APIRouter(prefix='/ast/item', dependencies=[Depends(LoginService.get_current_user)])


@astItemController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('ast:item:list'))]
)
async def get_ast_item_list(
    request: Request,
    ast_item_page_query: AstItemPageQueryModel = Depends(AstItemPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('AstItem')),
):
    # 获取分页数据
    item_page_query_result = await AstItemService.get_ast_item_list_services(
        query_db, ast_item_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=item_page_query_result)


@astItemController.get(
    '/{item_id}', response_model=AstItemDetailModel, dependencies=[Depends(CheckUserInterfaceAuth('ast:item:query'))]
)
async def query_detail_ast_item(
    request: Request,
    item_id: int, 
    query_db: AsyncSession = Depends(get_db)
):
    # 获取物品详情
    detail_item_result = await AstItemService.get_ast_item_detail_services(query_db, item_id)
    logger.info(f'获取item_id为{item_id}的信息成功')

    return ResponseUtil.success(model_content=detail_item_result)


@astItemController.post('', dependencies=[Depends(CheckUserInterfaceAuth('ast:item:add'))])
@ValidateFields(validate_model='add_ast_item')
@Log(title='物品管理', business_type=BusinessType.INSERT)
async def add_ast_item(
    request: Request,
    add_ast_item: AddAstItemModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 设置创建和更新信息
    add_ast_item.create_by = current_user.user.user_name
    add_ast_item.create_time = datetime.now()
    add_ast_item.update_by = current_user.user.user_name
    add_ast_item.update_time = datetime.now()
    # 新增物品信息
    add_ast_item_result = await AstItemService.add_ast_item_services(query_db, add_ast_item)
    logger.info(add_ast_item_result.message)

    return ResponseUtil.success(msg=add_ast_item_result.message)


@astItemController.put('', dependencies=[Depends(CheckUserInterfaceAuth('ast:item:edit'))])
@ValidateFields(validate_model='edit_ast_item')
@Log(title='物品管理', business_type=BusinessType.UPDATE)
async def edit_ast_item(
    request: Request,
    edit_ast_item: EditAstItemModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 设置更新信息
    edit_ast_item.update_by = current_user.user.user_name
    edit_ast_item.update_time = datetime.now()
    # 编辑物品信息
    edit_ast_item_result = await AstItemService.edit_ast_item_services(query_db, edit_ast_item)
    logger.info(edit_ast_item_result.message)

    return ResponseUtil.success(msg=edit_ast_item_result.message)


@astItemController.delete('/{item_ids}', dependencies=[Depends(CheckUserInterfaceAuth('ast:item:remove'))])
@Log(title='物品管理', business_type=BusinessType.DELETE)
async def delete_ast_item(
    request: Request,
    item_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 构建删除对象
    delete_ast_item = DeleteAstItemModel(
        itemIds=item_ids, updateBy=current_user.user.user_name, updateTime=datetime.now()
    )
    # 删除物品信息
    delete_ast_item_result = await AstItemService.delete_ast_item_services(query_db, delete_ast_item)
    logger.info(delete_ast_item_result.message)

    return ResponseUtil.success(msg=delete_ast_item_result.message)

