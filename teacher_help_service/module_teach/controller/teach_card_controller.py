from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_card_vo import (
    AddTeachCardModel,
    ChangeTeachCardStatusModel,
    DeleteTeachCardModel,
    EditTeachCardModel,
    GrantTeachCardModel,
    TeachCardGrantPageQueryModel,
    TeachCardLogPageQueryModel,
    TeachCardPageQueryModel,
    VoidTeachCardGrantModel,
)
from module_teach.service.teach_card_service import TeachCardService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachCardController = APIRouter(prefix='/teach/card', dependencies=[Depends(LoginService.get_current_user)])


# ------------------------ 卡模板 ------------------------
@teachCardController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:card:list'))]
)
async def get_teach_card_list(
    request: Request,
    card_page_query: TeachCardPageQueryModel = Depends(TeachCardPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCard')),
):
    card_page_result = await TeachCardService.get_teach_card_list_services(
        query_db, card_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=card_page_result)


# ------------------------ 发放记录 ------------------------
@teachCardController.get(
    '/grant/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:card:list'))]
)
async def get_teach_card_grant_list(
    request: Request,
    grant_page_query: TeachCardGrantPageQueryModel = Depends(TeachCardGrantPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCardGrant')),
):
    grant_page_result = await TeachCardService.get_teach_card_grant_list_services(
        query_db, grant_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=grant_page_result)


@teachCardController.post('/grant', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:grant'))])
@Log(title='会员卡发放', business_type=BusinessType.INSERT)
async def grant_teach_card(
    request: Request,
    grant_card: GrantTeachCardModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCardService.grant_teach_card_services(
        query_db, grant_card, current_user.user.user_id, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachCardController.put('/grant/void', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:grant'))])
@Log(title='会员卡作废', business_type=BusinessType.UPDATE)
async def void_teach_card_grant(
    request: Request,
    void_form: VoidTeachCardGrantModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCardService.void_teach_card_grant_services(
        query_db, void_form, current_user.user.user_id, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ------------------------ 操作记录 ------------------------
@teachCardController.get(
    '/log/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:card:list'))]
)
async def get_teach_card_log_list(
    request: Request,
    log_page_query: TeachCardLogPageQueryModel = Depends(TeachCardLogPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCardLog')),
):
    log_page_result = await TeachCardService.get_teach_card_log_list_services(
        query_db, log_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=log_page_result)


# ------------------------ 学员持卡 ------------------------
@teachCardController.get('/student/{student_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:list'))])
async def get_student_cards(request: Request, student_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachCardService.get_student_cards_services(query_db, student_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


# ------------------------ 卡模板 CRUD ------------------------
@teachCardController.get('/{card_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:query'))])
async def get_teach_card_detail(request: Request, card_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachCardService.get_teach_card_detail_services(query_db, card_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachCardController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:add'))])
@ValidateFields(validate_model='add_card')
@Log(title='会员卡管理', business_type=BusinessType.INSERT)
async def add_teach_card(
    request: Request,
    add_card: AddTeachCardModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCardService.add_teach_card_services(query_db, add_card, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachCardController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:edit'))])
@ValidateFields(validate_model='edit_card')
@Log(title='会员卡管理', business_type=BusinessType.UPDATE)
async def edit_teach_card(
    request: Request,
    edit_card: EditTeachCardModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCardService.edit_teach_card_services(query_db, edit_card, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCardController.put('/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:edit'))])
@Log(title='会员卡状态', business_type=BusinessType.UPDATE)
async def change_teach_card_status(
    request: Request,
    status_form: ChangeTeachCardStatusModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCardService.change_card_status_services(query_db, status_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCardController.delete('/{card_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:card:remove'))])
@Log(title='会员卡管理', business_type=BusinessType.DELETE)
async def delete_teach_card(
    request: Request,
    card_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_card = DeleteTeachCardModel(card_ids=card_ids)
    result = await TeachCardService.delete_teach_card_services(query_db, delete_card, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
