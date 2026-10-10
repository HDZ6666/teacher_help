from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.service.login_service import LoginService, CurrentUserModel
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.aspect.data_scope import GetDataScope
from module_teach.service.teach_enrollment_service import TeachEnrollmentService
from module_teach.service.teach_student_assign_service import TeachStudentAssignService
from module_teach.service.teach_student_service import TeachStudentService
from module_teach.entity.vo.teach_student_vo import (
    TeachStudentPageQueryModel,
    AddTeachStudentModel,
    EditTeachStudentModel,
    DeleteTeachStudentModel,
    TeachStudentResponseModel,
    TeachStudentDetailModel,
    TeachStudentEnrollModel,
    AssignTeachStudentStaffModel,
)
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel
from utils.common_util import bytes2file_response
from utils.log_util import logger


teachStudentController = APIRouter(prefix='/teach/student', dependencies=[Depends(LoginService.get_current_user)])


@teachStudentController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:student:list'))])
async def get_teach_student_list(
    request: Request,
    student_page_query: TeachStudentPageQueryModel = Depends(TeachStudentPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('TeachStudent'))
):
    """
    获取学生分页列表
    
    Args:
        request: 请求对象
        student_page_query: 分页查询参数
        query_db: 数据库会话
        current_user: 当前用户
        data_scope_sql: 数据权限SQL
        
    Returns:
        学生分页列表响应
    """
    # 获取分页数据
    student_page_query_result = await TeachStudentService.get_teach_student_list_services(
        query_db, student_page_query, data_scope_sql, is_page=True
    )
    await TeachStudentAssignService.fill_staff_names(query_db, student_page_query_result.rows)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=student_page_query_result)


@teachStudentController.get(
    '/staff-options', dependencies=[Depends(CheckUserInterfaceAuth(['teach:student:assign', 'teach:student:list']))]
)
async def get_teach_student_staff_options(
    request: Request,
    role: str,
    keyword: str = None,
    query_db: AsyncSession = Depends(get_db),
):
    """
    跟进人/学管师候选员工（系统员工账号），附已分配在读学员数
    """
    result = await TeachStudentAssignService.get_staff_options_services(query_db, role, keyword)
    return ResponseUtil.success(data=result)


@teachStudentController.put('/assign', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:assign'))])
@Log(title='学员分配跟进人/学管师', business_type=BusinessType.UPDATE)
async def assign_teach_student_staff(
    request: Request,
    assign_form: AssignTeachStudentStaffModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    批量分配跟进人/学管师（userId 为空表示改为待分配）
    """
    result = await TeachStudentAssignService.assign_services(
        query_db, assign_form.student_ids, assign_form.role, assign_form.user_id, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachStudentController.post('/enroll', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:edit'))])
@ValidateFields(validate_model='enroll_form')
@Log(title='学生报名续费', business_type=BusinessType.INSERT)
async def submit_student_enroll(
    request: Request,
    enroll_form: TeachStudentEnrollModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    提交学生报名/续费订单
    """
    enroll_result = await TeachEnrollmentService.submit_student_enroll_services(
        query_db, enroll_form, current_user.user.user_name
    )
    logger.info(enroll_result.message)

    return ResponseUtil.success(msg=enroll_result.message, data=enroll_result.result)


@teachStudentController.get(
    '/{student_id}/courses',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))],
)
async def get_student_courses(
    request: Request,
    student_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取学生报读课程
    """
    course_result = await TeachEnrollmentService.get_student_course_accounts_services(query_db, student_id)
    logger.info('获取成功')

    return ResponseUtil.success(data=course_result)


@teachStudentController.get(
    '/{student_id}/orders',
    dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))],
)
async def get_student_orders(
    request: Request,
    student_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取学生消费订单
    """
    order_result = await TeachEnrollmentService.get_student_orders_services(query_db, student_id)
    logger.info('获取成功')

    return ResponseUtil.success(data=order_result)


@teachStudentController.get('/{student_id}', response_model=TeachStudentDetailModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:student:query'))])
async def get_teach_student_detail(
    request: Request,
    student_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取学生详情
    
    Args:
        request: 请求对象
        student_id: 学生ID
        query_db: 数据库会话
        current_user: 当前用户
        
    Returns:
        学生详情响应
    """
    student_detail = await TeachStudentService.get_teach_student_detail_services(query_db, student_id)

    if student_detail.id:
        logger.info('获取成功')
        return ResponseUtil.success(data=student_detail.model_dump(by_alias=True))
    else:
        logger.warning('学生不存在')
        return ResponseUtil.failure(msg='学生不存在')


@teachStudentController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:add'))])
@ValidateFields(validate_model='add_student')
@Log(title='学生管理', business_type=BusinessType.INSERT)
async def add_teach_student(
    request: Request,
    add_student: AddTeachStudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    新增学生
    
    Args:
        request: 请求对象
        add_student: 新增学生模型
        query_db: 数据库会话
        current_user: 当前用户
        
    Returns:
        新增结果响应
    """
    add_result = await TeachStudentService.add_teach_student_services(query_db, add_student, current_user.user.user_name)
    logger.info(add_result.message)

    return ResponseUtil.success(msg=add_result.message)


@teachStudentController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:edit'))])
@ValidateFields(validate_model='edit_student')
@Log(title='学生管理', business_type=BusinessType.UPDATE)
async def edit_teach_student(
    request: Request,
    edit_student: EditTeachStudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    编辑学生
    
    Args:
        request: 请求对象
        edit_student: 编辑学生模型
        query_db: 数据库会话
        current_user: 当前用户
        
    Returns:
        编辑结果响应
    """
    edit_result = await TeachStudentService.edit_teach_student_services(query_db, edit_student, current_user.user.user_name)
    logger.info(edit_result.message)

    return ResponseUtil.success(msg=edit_result.message)


@teachStudentController.delete('/{student_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:remove'))])
@Log(title='学生管理', business_type=BusinessType.DELETE)
async def delete_teach_student(
    request: Request,
    student_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    删除学生

    Args:
        request: 请求对象
        student_ids: 学生ID，多个用逗号分隔
        query_db: 数据库会话
        current_user: 当前用户

    Returns:
        删除结果响应
    """
    # 创建删除模型对象
    delete_student = DeleteTeachStudentModel(ids=student_ids)
    delete_result = await TeachStudentService.delete_teach_student_services(query_db, delete_student, current_user.user.user_name)
    logger.info(delete_result.message)

    return ResponseUtil.success(msg=delete_result.message)


@teachStudentController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:export'))])
@Log(title='学生管理', business_type=BusinessType.EXPORT)
async def export_teach_student_list(
    request: Request,
    student_page_query: TeachStudentPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('TeachStudent'))
):
    """
    导出学生数据

    Args:
        request: 请求对象
        student_page_query: 查询参数
        query_db: 数据库会话
        current_user: 当前用户
        data_scope_sql: 数据权限SQL

    Returns:
        导出文件响应
    """
    # 获取全量数据
    student_query_result = await TeachStudentService.get_teach_student_list_services(
        query_db, student_page_query, data_scope_sql, is_page=False
    )
    student_export_result = await TeachStudentService.export_teach_student_list_services(student_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(student_export_result))


@teachStudentController.get('/parent/{parent_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:student:list'))])
async def get_students_by_parent(
    request: Request,
    parent_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    根据家长ID获取学生列表
    
    Args:
        request: 请求对象
        parent_id: 家长ID
        query_db: 数据库会话
        current_user: 当前用户
        
    Returns:
        学生列表响应
    """
    from module_teach.dao.teach_student_dao import TeachStudentDao
    students = await TeachStudentDao.get_teach_students_by_parent_id(query_db, parent_id)

    # 转换为响应格式
    student_list = []
    for student in students:
        student_dict = {
            'id': student.id,
            'student_name': student.student_name,
            'gender': student.gender,
            'birthday': student.birthday,
            'school_name': student.school_name,
            'grade': student.grade,
            'class_name': student.class_name,
            'status': student.status,
            'create_time': student.create_time
        }
        student_list.append(student_dict)

    logger.info('获取成功')
    return ResponseUtil.success(model_content=student_list)
