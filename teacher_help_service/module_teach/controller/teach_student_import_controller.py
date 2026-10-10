from typing import Literal
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.service.teach_student_import_service import TeachStudentImportService
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.response_util import ResponseUtil


teachStudentImportController = APIRouter(
    prefix='/teach/student-import', dependencies=[Depends(LoginService.get_current_user)]
)


@teachStudentImportController.post(
    '/template/{kind}', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:import'))]
)
async def download_student_import_template(
    request: Request, kind: Literal['student', 'lesson', 'month'], query_db: AsyncSession = Depends(get_db)
):
    """
    下载导入模板：student=学生基本信息 lesson=按课时报读 month=按月报读
    """
    result = await TeachStudentImportService.get_template_services(query_db, kind)
    logger.info('下载成功')
    return ResponseUtil.streaming(data=bytes2file_response(result))


@teachStudentImportController.post('/{kind}', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:import'))])
@Log(title='学员导入', business_type=BusinessType.IMPORT)
async def import_students(
    request: Request,
    kind: Literal['student', 'lesson', 'month'],
    file: UploadFile = File(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    导入：整表校验通过才写入；失败时 data.success=false 并返回错误行
    """
    result = await TeachStudentImportService.import_services(query_db, kind, file, current_user.user.user_name)
    if result['success']:
        message = f'导入成功，共{result["successCount"]}行'
    else:
        message = f'校验未通过，共{result["errorCount"]}行有误，未导入任何数据'
    logger.info(message)
    return ResponseUtil.success(msg=message, data=result)
