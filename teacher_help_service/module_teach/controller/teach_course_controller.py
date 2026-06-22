from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_course_vo import (
    AddTeachCourseModel,
    AddTeachCoursePackageModel,
    BatchAddTeachCourseModel,
    ChangeTeachCourseStatusModel,
    ChangeTeachPackageStatusModel,
    DeleteTeachCoursePackageModel,
    DeleteTeachCourseModel,
    EditTeachCourseModel,
    EditTeachCoursePackageModel,
    TeachCoursePackagePageQueryModel,
    TeachCoursePageQueryModel,
)
from module_teach.service.teach_course_service import TeachCourseService
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachCourseController = APIRouter(prefix='/teach/course', dependencies=[Depends(LoginService.get_current_user)])


@teachCourseController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:course:list'))]
)
async def get_teach_course_list(
    request: Request,
    course_page_query: TeachCoursePageQueryModel = Depends(TeachCoursePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCourse')),
):
    course_page_result = await TeachCourseService.get_teach_course_list_services(
        query_db, course_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=course_page_result)


@teachCourseController.get(
    '/options',
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:course:list', 'ast:item:list', 'ast:fee:list']))],
)
async def get_course_options(request: Request, keyword: str | None = None, query_db: AsyncSession = Depends(get_db)):
    result = await TeachCourseService.get_course_options_services(query_db, keyword)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachCourseController.get(
    '/package/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('teach:course:list'))],
)
async def get_teach_package_list(
    request: Request,
    package_page_query: TeachCoursePackagePageQueryModel = Depends(TeachCoursePackagePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCoursePackage')),
):
    package_page_result = await TeachCourseService.get_teach_package_list_services(
        query_db, package_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=package_page_result)


@teachCourseController.get('/package/{package_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:query'))])
async def get_teach_package_detail(request: Request, package_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachCourseService.get_teach_package_detail_services(query_db, package_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachCourseController.post('/package', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:add'))])
@ValidateFields(validate_model='add_package')
@Log(title='课程套餐', business_type=BusinessType.INSERT)
async def add_teach_package(
    request: Request,
    add_package: AddTeachCoursePackageModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.add_teach_package_services(query_db, add_package, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachCourseController.put('/package', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:edit'))])
@ValidateFields(validate_model='edit_package')
@Log(title='课程套餐', business_type=BusinessType.UPDATE)
async def edit_teach_package(
    request: Request,
    edit_package: EditTeachCoursePackageModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.edit_teach_package_services(query_db, edit_package, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCourseController.put('/package/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:edit'))])
@Log(title='课程套餐状态', business_type=BusinessType.UPDATE)
async def change_teach_package_status(
    request: Request,
    status_form: ChangeTeachPackageStatusModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.change_package_status_services(query_db, status_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCourseController.delete('/package/{package_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:remove'))])
@Log(title='课程套餐', business_type=BusinessType.DELETE)
async def delete_teach_package(
    request: Request,
    package_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_package = DeleteTeachCoursePackageModel(package_ids=package_ids)
    result = await TeachCourseService.delete_teach_package_services(
        query_db, delete_package, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCourseController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth(['teach:course:export', 'teach:course:list']))])
@Log(title='课程管理', business_type=BusinessType.EXPORT)
async def export_teach_course_list(
    request: Request,
    course_page_query: TeachCoursePageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCourse')),
):
    course_result = await TeachCourseService.get_teach_course_list_services(
        query_db, course_page_query, data_scope_sql, is_page=False
    )
    export_result = await TeachCourseService.export_teach_course_list_services(course_result)
    logger.info('导出成功')
    return ResponseUtil.streaming(data=bytes2file_response(export_result))


@teachCourseController.post('/batch', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:add'))])
@Log(title='课程管理', business_type=BusinessType.INSERT)
async def batch_add_teach_course(
    request: Request,
    batch_course: BatchAddTeachCourseModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.batch_add_teach_course_services(
        query_db, batch_course, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachCourseController.get('/{course_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:query'))])
async def get_teach_course_detail(request: Request, course_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachCourseService.get_teach_course_detail_services(query_db, course_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachCourseController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:add'))])
@ValidateFields(validate_model='add_course')
@Log(title='课程管理', business_type=BusinessType.INSERT)
async def add_teach_course(
    request: Request,
    add_course: AddTeachCourseModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.add_teach_course_services(query_db, add_course, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachCourseController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:edit'))])
@ValidateFields(validate_model='edit_course')
@Log(title='课程管理', business_type=BusinessType.UPDATE)
async def edit_teach_course(
    request: Request,
    edit_course: EditTeachCourseModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.edit_teach_course_services(query_db, edit_course, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCourseController.put('/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:edit'))])
@Log(title='课程状态', business_type=BusinessType.UPDATE)
async def change_teach_course_status(
    request: Request,
    status_form: ChangeTeachCourseStatusModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachCourseService.change_course_status_services(query_db, status_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachCourseController.delete('/{course_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:course:remove'))])
@Log(title='课程管理', business_type=BusinessType.DELETE)
async def delete_teach_course(
    request: Request,
    course_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_course = DeleteTeachCourseModel(course_ids=course_ids)
    result = await TeachCourseService.delete_teach_course_services(query_db, delete_course, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
