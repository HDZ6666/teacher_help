from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_student_account_vo import (
    ChangeCourseValidityModel,
    ClearCourseAccountModel,
    CompleteCourseAccountModel,
    ResumeCourseAccountModel,
    StopCourseAccountModel,
    TeachCourseAccountPageQueryModel,
    TransferCourseAccountModel,
)
from module_teach.service.teach_student_account_service import TeachStudentAccountService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachStudentAccountController = APIRouter(
    prefix='/teach/student-account', dependencies=[Depends(LoginService.get_current_user)]
)


@teachStudentAccountController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:student:list'))]
)
async def get_course_account_list(
    request: Request,
    page_query: TeachCourseAccountPageQueryModel = Depends(TeachCourseAccountPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """
    报读情况（学员课程账户）分页列表
    """
    result = await TeachStudentAccountService.get_account_list_services(query_db, page_query)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachStudentAccountController.get('/logs', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))])
async def get_course_account_logs(
    request: Request,
    student_id: int = Query(default=None, alias='studentId'),
    account_id: int = Query(default=None, alias='accountId'),
    query_db: AsyncSession = Depends(get_db),
):
    """
    课程账户操作日志（转课/清零/有效期/停课/复课/结课/导入）
    """
    result = await TeachStudentAccountService.get_account_logs_services(query_db, student_id, account_id)
    return ResponseUtil.success(data=result)


@teachStudentAccountController.post(
    '/transfer', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:account'))]
)
@Log(title='学员批量转课', business_type=BusinessType.UPDATE)
async def transfer_course_account(
    request: Request,
    form: TransferCourseAccountModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentAccountService.transfer_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentAccountController.post('/clear', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:account'))])
@Log(title='学员批量课时清零', business_type=BusinessType.UPDATE)
async def clear_course_account(
    request: Request,
    form: ClearCourseAccountModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentAccountService.clear_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentAccountController.post(
    '/validity', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:account'))]
)
@Log(title='学员批量修改课程有效期', business_type=BusinessType.UPDATE)
async def change_course_validity(
    request: Request,
    form: ChangeCourseValidityModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentAccountService.change_validity_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentAccountController.post('/stop', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:account'))])
@Log(title='学员停课', business_type=BusinessType.UPDATE)
async def stop_course_account(
    request: Request,
    form: StopCourseAccountModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentAccountService.stop_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentAccountController.post('/resume', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:account'))])
@Log(title='学员复课', business_type=BusinessType.UPDATE)
async def resume_course_account(
    request: Request,
    form: ResumeCourseAccountModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentAccountService.resume_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentAccountController.post(
    '/complete', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:account'))]
)
@Log(title='学员结课', business_type=BusinessType.UPDATE)
async def complete_course_account(
    request: Request,
    form: CompleteCourseAccountModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachStudentAccountService.complete_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachStudentAccountController.get(
    '/receipt/{order_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))]
)
async def get_order_receipt(request: Request, order_id: int, query_db: AsyncSession = Depends(get_db)):
    """
    缴费收据数据（前端打印）
    """
    result = await TeachStudentAccountService.get_receipt_services(query_db, order_id)
    return ResponseUtil.success(data=result)


@teachStudentAccountController.get(
    '/student/{student_id}/lessons', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))]
)
async def get_student_lessons(
    request: Request,
    student_id: int,
    page_num: int = Query(default=1, alias='pageNum', ge=1),
    page_size: int = Query(default=10, alias='pageSize', ge=1, le=100),
    query_db: AsyncSession = Depends(get_db),
):
    """
    学员详情-上课记录（班级点名明细）
    """
    result = await TeachStudentAccountService.get_student_lessons_services(query_db, student_id, page_num, page_size)
    return ResponseUtil.success(model_content=result)


@teachStudentAccountController.get(
    '/student/{student_id}/checkins', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))]
)
async def get_student_checkins(
    request: Request,
    student_id: int,
    page_num: int = Query(default=1, alias='pageNum', ge=1),
    page_size: int = Query(default=10, alias='pageSize', ge=1, le=100),
    query_db: AsyncSession = Depends(get_db),
):
    """
    学员详情-考勤记录（课表签到）
    """
    result = await TeachStudentAccountService.get_student_checkins_services(query_db, student_id, page_num, page_size)
    return ResponseUtil.success(model_content=result)


@teachStudentAccountController.get(
    '/student/{student_id}/comments', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))]
)
async def get_student_comments(
    request: Request,
    student_id: int,
    page_num: int = Query(default=1, alias='pageNum', ge=1),
    page_size: int = Query(default=10, alias='pageSize', ge=1, le=100),
    query_db: AsyncSession = Depends(get_db),
):
    """
    学员详情-成长档案（已发布的课后点评）
    """
    result = await TeachStudentAccountService.get_student_comments_services(query_db, student_id, page_num, page_size)
    return ResponseUtil.success(model_content=result)
