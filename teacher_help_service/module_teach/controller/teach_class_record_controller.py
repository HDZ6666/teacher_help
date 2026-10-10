from fastapi import APIRouter, Depends, Form, Request
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
    MarkMakeupModel,
    RevokeClassAttendanceModel,
)
from module_teach.entity.vo.teach_lesson_vo import (
    EditAttendanceDetailModel,
    EditAttendanceRecordModel,
    MakeupClassModel,
)
from module_teach.service.teach_class_record_service import TeachClassRecordService
from module_teach.service.teach_class_service import TeachClassService
from module_teach.service.teach_lesson_service import TeachLessonService
from utils.common_util import bytes2file_response
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


async def _export_records(query_db: AsyncSession, record_type: str, query_object):
    binary_data = await TeachClassRecordService.export_record_list_services(query_db, record_type, query_object)
    logger.info('导出成功')
    return ResponseUtil.streaming(data=bytes2file_response(binary_data))


@teachClassRecordController.post(
    '/attendance/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:export'))]
)
@Log(title='点名记录导出', business_type=BusinessType.EXPORT)
async def export_attendance_record_list(
    request: Request,
    query_object: ClassRecordAttendanceQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    return await _export_records(query_db, 'attendance', query_object)


@teachClassRecordController.post(
    '/overtime/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:export'))]
)
@Log(title='超时未点名导出', business_type=BusinessType.EXPORT)
async def export_overtime_record_list(
    request: Request,
    query_object: ClassRecordOvertimeQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    return await _export_records(query_db, 'overtime', query_object)


@teachClassRecordController.post(
    '/makeup/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:export'))]
)
@Log(title='补课记录导出', business_type=BusinessType.EXPORT)
async def export_makeup_record_list(
    request: Request,
    query_object: ClassRecordMakeupQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    return await _export_records(query_db, 'makeup', query_object)


@teachClassRecordController.post(
    '/absence/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:export'))]
)
@Log(title='缺课提醒导出', business_type=BusinessType.EXPORT)
async def export_absence_record_list(
    request: Request,
    query_object: ClassRecordAbsenceQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    return await _export_records(query_db, 'absence', query_object)


@teachClassRecordController.put(
    '/makeup/mark', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:makeup'))]
)
@Log(title='缺课标记已补', business_type=BusinessType.UPDATE)
async def mark_makeup_record(
    request: Request,
    mark_form: MarkMakeupModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassRecordService.mark_makeup_services(
        query_db, mark_form.ids, mark_form.remark, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassRecordController.put(
    '/attendance/detail', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:editDetail'))]
)
@Log(title='修改单个学员点名', business_type=BusinessType.UPDATE)
async def edit_attendance_detail(
    request: Request,
    edit_form: EditAttendanceDetailModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.edit_detail_services(query_db, edit_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassRecordController.put('/attendance', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:edit'))])
@Log(title='编辑课次', business_type=BusinessType.UPDATE)
async def edit_attendance_record(
    request: Request,
    edit_form: EditAttendanceRecordModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.edit_record_services(query_db, edit_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassRecordController.post(
    '/makeup/class', dependencies=[Depends(CheckUserInterfaceAuth('teach:classRecord:makeupClass'))]
)
@Log(title='开补课班', business_type=BusinessType.INSERT)
async def create_makeup_class(
    request: Request,
    makeup_form: MakeupClassModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.makeup_class_services(query_db, makeup_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)
