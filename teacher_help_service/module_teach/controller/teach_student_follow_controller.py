from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_student_account_vo import TeachStudentFollowModel, TeachStudentFollowPageQueryModel
from module_teach.service.teach_student_follow_service import TeachStudentFollowService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachStudentFollowController = APIRouter(
    prefix='/teach/student-follow', dependencies=[Depends(LoginService.get_current_user)]
)


@teachStudentFollowController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))]
)
async def get_student_follow_list(
    request: Request,
    page_query: TeachStudentFollowPageQueryModel = Depends(TeachStudentFollowPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """
    学员跟进记录分页列表
    """
    result = await TeachStudentFollowService.get_follow_list_services(query_db, page_query)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachStudentFollowController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:follow'))])
@Log(title='学员跟进记录', business_type=BusinessType.INSERT)
async def add_student_follow(
    request: Request,
    form: TeachStudentFollowModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    form.id = None
    result = await TeachStudentFollowService.save_follow_services(query_db, form, current_user.user)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentFollowController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:follow'))])
@Log(title='学员跟进记录', business_type=BusinessType.UPDATE)
async def edit_student_follow(
    request: Request,
    form: TeachStudentFollowModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    if not form.id:
        return ResponseUtil.failure(msg='缺少跟进记录ID')
    result = await TeachStudentFollowService.save_follow_services(query_db, form, current_user.user)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentFollowController.delete(
    '/{follow_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:follow'))]
)
@Log(title='学员跟进记录', business_type=BusinessType.DELETE)
async def delete_student_follow(
    request: Request,
    follow_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentFollowService.delete_follow_services(query_db, follow_ids, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
