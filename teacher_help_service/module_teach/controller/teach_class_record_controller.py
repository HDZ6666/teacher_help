from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_class_record_vo import (
    ClassRecordAbsenceQueryModel,
    ClassRecordAttendanceQueryModel,
    ClassRecordMakeupQueryModel,
    ClassRecordOvertimeQueryModel,
    RevokeClassAttendanceModel,
)
from module_teach.service.teach_class_record_service import TeachClassRecordService
from module_teach.service.teach_class_service import TeachClassService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachClassRecordController = APIRouter(
    prefix='/teach/class-record', dependencies=[Depends(LoginService.get_current_user)]
)


@teachClassRecordController.get(
    '/attendance/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:classRecord:list', 'teach:class:query']))],
)
async def get_attendance_record_list(
    request: Request,
    query_object: ClassRecordAttendanceQueryModel = Depends(ClassRecordAttendanceQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassRecordService.get_attendance_list_services(query_db, query_object)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachClassRecordController.put(
    '/attendance/revoke', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:revoke'))]
)
@Log(title='撤销点名', business_type=BusinessType.UPDATE)
async def revoke_attendance_record(
    request: Request,
    revoke_form: RevokeClassAttendanceModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassService.revoke_class_attendance_services(
        query_db, revoke_form.id, revoke_form.reason, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassRecordController.get(
    '/attendance/{record_id}',
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:classRecord:query', 'teach:class:query']))],
)
async def get_attendance_record_detail(
    request: Request,
    record_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassRecordService.get_attendance_detail_services(query_db, record_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachClassRecordController.get(
    '/overtime/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:classRecord:list', 'teach:schedule:event:list']))],
)
async def get_overtime_record_list(
    request: Request,
    query_object: ClassRecordOvertimeQueryModel = Depends(ClassRecordOvertimeQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassRecordService.get_overtime_list_services(query_db, query_object)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachClassRecordController.get(
    '/makeup/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:classRecord:list', 'teach:class:query']))],
)
async def get_makeup_record_list(
    request: Request,
    query_object: ClassRecordMakeupQueryModel = Depends(ClassRecordMakeupQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassRecordService.get_makeup_list_services(query_db, query_object)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachClassRecordController.get(
    '/absence/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth(['teach:classRecord:list', 'teach:class:query']))],
)
async def get_absence_record_list(
    request: Request,
    query_object: ClassRecordAbsenceQueryModel = Depends(ClassRecordAbsenceQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachClassRecordService.get_absence_list_services(query_db, query_object)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)
