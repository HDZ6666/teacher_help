from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_comment_vo import (
    AddTeachCommentModel,
    BatchTeachCommentModel,
    DeleteTeachCommentModel,
    EditTeachCommentModel,
    TeachCommentPageQueryModel,
)
from module_teach.service.teach_comment_service import TeachCommentService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachCommentController = APIRouter(prefix='/teach/comment', dependencies=[Depends(LoginService.get_current_user)])


@teachCommentController.get(
    '/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:list'))],
)
async def get_teach_comment_list(
    request: Request,
    query_object: TeachCommentPageQueryModel = Depends(TeachCommentPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取课后点评分页列表
    """
    result = await TeachCommentService.get_comment_list_services(query_db, query_object)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachCommentController.get(
    '/pending',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:query'))],
)
async def get_pending_students(
    request: Request,
    attendance_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取某次点名下未点评学员列表
    """
    result = await TeachCommentService.get_pending_students_services(query_db, attendance_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachCommentController.get(
    '/{comment_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:query'))],
)
async def get_teach_comment_detail(
    request: Request,
    comment_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取课后点评详情
    """
    result = await TeachCommentService.get_comment_detail_services(query_db, comment_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachCommentController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:add'))])
@Log(title='课后点评', business_type=BusinessType.INSERT)
async def add_teach_comment(
    request: Request,
    add_comment: AddTeachCommentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    发布点评(单个)
    """
    result = await TeachCommentService.add_comment_services(query_db, add_comment, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCommentController.post('/batch', dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:add'))])
@Log(title='课后点评', business_type=BusinessType.INSERT)
async def batch_teach_comment(
    request: Request,
    batch_comment: BatchTeachCommentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    批量/统一点评(一组学员用同一内容)
    """
    result = await TeachCommentService.batch_comment_services(query_db, batch_comment, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCommentController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:edit'))])
@Log(title='课后点评', business_type=BusinessType.UPDATE)
async def edit_teach_comment(
    request: Request,
    edit_comment: EditTeachCommentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    编辑点评
    """
    result = await TeachCommentService.edit_comment_services(query_db, edit_comment, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCommentController.delete('/{comment_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:comment:remove'))])
@Log(title='课后点评', business_type=BusinessType.DELETE)
async def delete_teach_comment(
    request: Request,
    comment_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    撤销点评
    """
    delete_comment = DeleteTeachCommentModel(ids=comment_ids)
    result = await TeachCommentService.delete_comment_services(query_db, delete_comment, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
