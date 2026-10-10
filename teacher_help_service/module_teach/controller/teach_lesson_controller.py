from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_lesson_vo import AddTempStudentModel, RescheduleLessonModel, WeeklyScheduleModel
from module_teach.service.teach_lesson_service import TeachLessonService
from utils.log_util import logger
from utils.response_util import ResponseUtil


teachLessonController = APIRouter(
    prefix='/teach/schedule/lesson', dependencies=[Depends(LoginService.get_current_user)]
)


@teachLessonController.put(
    '/reschedule', dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:reschedule'))]
)
@Log(title='课次调课', business_type=BusinessType.UPDATE)
async def reschedule_lesson(
    request: Request,
    form: RescheduleLessonModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.reschedule_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachLessonController.get(
    '/temp-student/options', dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:temp'))]
)
async def get_temp_student_options(
    request: Request,
    event_id: int = Query(alias='eventId'),
    keyword: str | None = None,
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachLessonService.get_temp_student_options_services(query_db, event_id, keyword)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachLessonController.post(
    '/temp-student', dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:temp'))]
)
@Log(title='课次添加临时学员', business_type=BusinessType.INSERT)
async def add_temp_student(
    request: Request,
    form: AddTempStudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.add_temp_student_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachLessonController.delete(
    '/temp-student/{event_id}/{student_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:temp'))],
)
@Log(title='课次移出临时学员', business_type=BusinessType.DELETE)
async def remove_temp_student(
    request: Request,
    event_id: int,
    student_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.remove_temp_student_services(
        query_db, event_id, student_id, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachLessonController.post('/weekly', dependencies=[Depends(CheckUserInterfaceAuth('teach:schedule:event:batch'))])
@Log(title='班级按周重复排课', business_type=BusinessType.INSERT)
async def weekly_schedule(
    request: Request,
    form: WeeklyScheduleModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachLessonService.weekly_schedule_services(query_db, form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)
