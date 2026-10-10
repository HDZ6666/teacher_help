from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_teacher_permission_vo import SaveTeacherPermissionModel
from module_teach.service.teach_teacher_permission_service import TeachTeacherPermissionService
from utils.log_util import logger
from utils.response_util import ResponseUtil


teachTeacherPermissionController = APIRouter(
    prefix='/teach/teacher-permission', dependencies=[Depends(LoginService.get_current_user)]
)


@teachTeacherPermissionController.get(
    '/roles', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:permission'))]
)
async def get_permission_roles(request: Request, query_db: AsyncSession = Depends(get_db)):
    result = await TeachTeacherPermissionService.get_roles_services(query_db)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachTeacherPermissionController.get(
    '/role/{role_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:permission'))]
)
async def get_role_permission_tree(request: Request, role_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachTeacherPermissionService.get_role_tree_services(query_db, role_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachTeacherPermissionController.put(
    '/role', dependencies=[Depends(CheckUserInterfaceAuth('teach:teacher:permission'))]
)
@Log(title='老师权限配置', business_type=BusinessType.GRANT)
async def save_role_permission(
    request: Request,
    form: SaveTeacherPermissionModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachTeacherPermissionService.save_role_menus_services(
        query_db, form.role_id, form.menu_ids, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)
