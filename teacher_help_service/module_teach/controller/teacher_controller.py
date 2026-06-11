from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.service.login_service import LoginService, CurrentUserModel
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.aspect.data_scope import GetDataScope
from module_teach.service.teach_teacher_service import TeachTeacherService
from module_teach.entity.vo.teach_teacher_vo import (
    TeachTeacherPageQueryModel,
    AddTeachTeacherModel,
    EditTeachTeacherModel,
    DeleteTeachTeacherModel,
    TeachTeacherDetailModel
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.common_util import bytes2file_response
from utils.log_util import logger


teacherController = APIRouter(prefix='/teach/teacher', dependencies=[Depends(LoginService.get_current_user)])


@teacherController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:list'))]
)
async def get_teacher_list(
    request: Request,
    teacher_page_query: TeachTeacherPageQueryModel = Depends(TeachTeacherPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachTeacher'))
):
    """
    获取教师分页列表
    """
    # 获取分页数据
    teacher_page_query_result = await TeachTeacherService.get_teach_teacher_list_services(
        query_db, teacher_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=teacher_page_query_result)


@teacherController.get(
    '/{teacher_id}', response_model=TeachTeacherDetailModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:query'))]
)
async def get_teacher_detail(
    request: Request,
    teacher_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """
    获取教师详情
    """
    teacher_detail = await TeachTeacherService.get_teach_teacher_detail_services(query_db, teacher_id)
    logger.info('获取成功')

    return ResponseUtil.success(data=teacher_detail.model_dump(by_alias=True))


@teacherController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:add'))])
@ValidateFields(validate_model='add_teacher')
@Log(title='教师管理', business_type=BusinessType.INSERT)
async def add_teacher(
    request: Request,
    add_teacher: AddTeachTeacherModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    新增教师
    """
    add_result = await TeachTeacherService.add_teach_teacher_services(
        query_db, add_teacher, current_user.user.user_name
    )
    logger.info(add_result.message)

    return ResponseUtil.success(msg=add_result.message)


@teacherController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:edit'))])
@ValidateFields(validate_model='edit_teacher')
@Log(title='教师管理', business_type=BusinessType.UPDATE)
async def edit_teacher(
    request: Request,
    edit_teacher: EditTeachTeacherModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    编辑教师
    """
    edit_result = await TeachTeacherService.edit_teach_teacher_services(
        query_db, edit_teacher, current_user.user.user_name
    )
    logger.info(edit_result.message)

    return ResponseUtil.success(msg=edit_result.message)


@teacherController.delete('/{teacher_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:remove'))])
@Log(title='教师管理', business_type=BusinessType.DELETE)
async def delete_teacher(
    request: Request,
    teacher_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    删除教师
    """
    delete_teacher = DeleteTeachTeacherModel(ids=teacher_ids)
    delete_result = await TeachTeacherService.delete_teach_teacher_services(
        query_db, delete_teacher, current_user.user.user_name
    )
    logger.info(delete_result.message)

    return ResponseUtil.success(msg=delete_result.message)


@teacherController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:export'))])
@Log(title='教师管理', business_type=BusinessType.EXPORT)
async def export_teacher_list(
    request: Request,
    teacher_page_query: TeachTeacherPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachTeacher'))
):
    """
    导出教师列表
    """
    # 获取全量数据
    teacher_query_result = await TeachTeacherService.get_teach_teacher_list_services(
        query_db, teacher_page_query, data_scope_sql, is_page=False
    )
    teacher_export_result = await TeachTeacherService.export_teach_teacher_list_services(teacher_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(teacher_export_result))

