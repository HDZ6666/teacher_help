from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_class_vo import (
    AddTeachClassModel,
    AddTeachClassStudentModel,
    ChangeTeachClassRechargeModel,
    DeleteTeachClassModel,
    EditTeachClassModel,
    RemoveTeachClassStudentModel,
    SubmitTeachClassAttendanceModel,
    TeachClassPageQueryModel,
)
from module_teach.service.teach_class_service import TeachClassService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachClassController = APIRouter(prefix='/teach/class', dependencies=[Depends(LoginService.get_current_user)])


@teachClassController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:class:list'))]
)
async def get_teach_class_list(
    request: Request,
    class_page_query: TeachClassPageQueryModel = Depends(TeachClassPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachClass')),
):
    class_page_result = await TeachClassService.get_teach_class_list_services(
        query_db, class_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=class_page_result)


@teachClassController.get(
    '/options',
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:class:list', 'teach:student:edit']))],
)
async def get_teach_class_options(
    request: Request,
    course_id: int | None = None,
    keyword: str | None = None,
    class_mode: str | None = None,
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassService.get_teach_class_options_services(query_db, course_id, keyword, class_mode)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.get('/{class_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:query'))])
async def get_teach_class_detail(request: Request, class_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachClassService.get_teach_class_detail_services(query_db, class_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.get(
    '/{class_id}/students',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:query'))],
)
async def get_teach_class_students(request: Request, class_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachClassService.get_class_students_services(query_db, class_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.get(
    '/{class_id}/available-students',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:edit'))],
)
async def get_available_students(
    request: Request,
    class_id: int,
    keyword: str | None = None,
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassService.get_available_students_services(query_db, class_id, keyword)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.get(
    '/{class_id}/attendance/prepare',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:query'))],
)
async def get_class_attendance_prepare(
    request: Request,
    class_id: int,
    event_id: int | None = Query(default=None, alias='eventId'),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassService.get_attendance_prepare_services(query_db, class_id, event_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.get(
    '/{class_id}/attendance/list',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:query'))],
)
async def get_class_attendance_list(request: Request, class_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachClassService.get_class_attendance_list_services(query_db, class_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.get(
    '/attendance/{attendance_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:query'))],
)
async def get_class_attendance_detail(request: Request, attendance_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachClassService.get_class_attendance_detail_services(query_db, attendance_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:add'))])
@ValidateFields(validate_model='add_class')
@Log(title='班级管理', business_type=BusinessType.INSERT)
async def add_teach_class(
    request: Request,
    add_class: AddTeachClassModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassService.add_teach_class_services(query_db, add_class, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:edit'))])
@ValidateFields(validate_model='edit_class')
@Log(title='班级管理', business_type=BusinessType.UPDATE)
async def edit_teach_class(
    request: Request,
    edit_class: EditTeachClassModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassService.edit_teach_class_services(query_db, edit_class, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachClassController.put('/changeRecharge', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:edit'))])
@Log(title='班级充值购时', business_type=BusinessType.UPDATE)
async def change_teach_class_recharge(
    request: Request,
    recharge_form: ChangeTeachClassRechargeModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassService.change_recharge_services(query_db, recharge_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachClassController.post(
    '/{class_id}/students',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:edit'))],
)
@ValidateFields(validate_model='add_students')
@Log(title='班级学员', business_type=BusinessType.INSERT)
async def add_teach_class_students(
    request: Request,
    class_id: int,
    add_students: AddTeachClassStudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassService.add_class_students_services(
        query_db, class_id, add_students, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassController.post(
    '/{class_id}/attendance',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:edit'))],
)
@ValidateFields(validate_model='attendance_form')
@Log(title='班级点名', business_type=BusinessType.INSERT)
async def submit_class_attendance(
    request: Request,
    class_id: int,
    attendance_form: SubmitTeachClassAttendanceModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassService.submit_class_attendance_services(
        query_db, class_id, attendance_form, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassController.delete(
    '/{class_id}/students/{student_ids}',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:class:edit'))],
)
@Log(title='班级学员', business_type=BusinessType.DELETE)
async def remove_teach_class_students(
    request: Request,
    class_id: int,
    student_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    remove_students = RemoveTeachClassStudentModel(student_ids=student_ids)
    result = await TeachClassService.remove_class_students_services(
        query_db, class_id, remove_students, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassController.delete('/{class_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:remove'))])
@Log(title='班级管理', business_type=BusinessType.DELETE)
async def delete_teach_class(
    request: Request,
    class_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_class = DeleteTeachClassModel(class_ids=class_ids)
    result = await TeachClassService.delete_teach_class_services(
        query_db, delete_class, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
