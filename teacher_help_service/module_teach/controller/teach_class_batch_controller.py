from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_student_account_vo import ClassBatchIdsModel, ClassPromoteModel
from module_teach.service.teach_class_batch_service import TeachClassBatchService
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.response_util import ResponseUtil


teachClassBatchController = APIRouter(
    prefix='/teach/class-batch', dependencies=[Depends(LoginService.get_current_user)]
)


@teachClassBatchController.post(
    '/import/template', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:import'))]
)
async def download_class_import_template(request: Request, query_db: AsyncSession = Depends(get_db)):
    result = await TeachClassBatchService.get_import_template_services(query_db)
    logger.info('下载成功')
    return ResponseUtil.streaming(data=bytes2file_response(result))


@teachClassBatchController.post('/import', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:import'))])
@Log(title='班级导入', business_type=BusinessType.IMPORT)
async def import_classes(
    request: Request,
    file: UploadFile = File(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassBatchService.import_services(query_db, file, current_user.user.user_name)
    if result['success']:
        message = f'导入成功，共{result["successCount"]}个班级'
    else:
        message = f'校验未通过，共{result["errorCount"]}行有误，未导入任何数据'
    logger.info(message)
    return ResponseUtil.success(msg=message, data=result)


@teachClassBatchController.post('/promote', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:promote'))])
@Log(title='班级批量升班', business_type=BusinessType.UPDATE)
async def promote_classes(
    request: Request,
    form: ClassPromoteModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassBatchService.promote_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachClassBatchController.post('/graduate', dependencies=[Depends(CheckUserInterfaceAuth('teach:class:graduate'))])
@Log(title='班级批量结业', business_type=BusinessType.UPDATE)
async def graduate_classes(
    request: Request,
    form: ClassBatchIdsModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachClassBatchService.graduate_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)
