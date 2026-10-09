from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_schedule_attendance_dao import TeachScheduleAttendanceDao
from module_teach.dao.teach_schedule_event_dao import TeachScheduleEventDao
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.entity.do.teach_class_do import (
    TeachClass,
    TeachClassAttendance,
    TeachClassAttendanceDetail,
    TeachClassStudent,
    TeachClassTeacher,
)
from module_teach.entity.do.teach_enrollment_order_do import TeachEnrollmentOrderItem, TeachStudentCourseAccount
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
from exceptions.exception import ServiceException
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachClassService:
    """
    班级管理模块服务层
    """

    CLASS_MODE_LABELS = {
        'group': '班课',
        'one_to_one': '一对一',
    }
    CLASS_TYPE_LABELS = {
        'system': '系统班型',
        'custom': '自建班型',
    }
    ENROLL_STATUS_LABELS = {
        1: '招生中',
        2: '已满员',
        3: '已结课',
    }
    GENDER_LABELS = {
        '0': '男',
        '1': '女',
        '2': '未知',
        0: '男',
        1: '女',
        2: '未知',
    }
    ATTENDANCE_STATUS_LABELS = {
        1: '到课',
        2: '迟到',
        3: '请假',
        4: '未到',
    }
    # 班级点名表(teach_class_attendance_detail) status -> 课表考勤表(teach_schedule_attendances) status 映射
    # 新表: 1到课 2迟到 3请假 4未到
    # 旧表: 0未到 1出勤 2迟到 3请假 4缺勤
    # 说明: 新表的"4未到"在写入旧表时统一落到"4缺勤"。
    #       班级点名属于"应到名单内未到课"的场景, 语义上等价于旧表的"缺勤(应到未到)",
    #       而非旧表的"0未到"(多用于尚未考勤/无名单的初始态), 故选 4 而不是 0。
    CLASS_TO_SCHEDULE_STATUS_MAP = {
        1: 1,  # 到课 -> 出勤
        2: 2,  # 迟到 -> 迟到
        3: 3,  # 请假 -> 请假
        4: 4,  # 未到 -> 缺勤
    }
    # 旧表 status -> 新表 status 反向映射(读取旧表数据回填新表表单时用)
    # 旧表 0未到 没有"无名单初始态"的新表对应值, 统一回退到新表"4未到"。
    SCHEDULE_TO_CLASS_STATUS_MAP = {
        0: 4,  # 未到 -> 未到
        1: 1,  # 出勤 -> 到课
        2: 2,  # 迟到 -> 迟到
        3: 3,  # 请假 -> 请假
        4: 4,  # 缺勤 -> 未到
    }

    @classmethod
    def map_class_status_to_schedule(cls, class_status):
        """班级点名 status 映射为课表考勤 status, 无法识别时按"缺勤"处理。"""
        return cls.CLASS_TO_SCHEDULE_STATUS_MAP.get(class_status, 4)

    @classmethod
    def map_schedule_status_to_class(cls, schedule_status):
        """课表考勤 status 映射为班级点名 status, 无法识别时按"未到"处理。"""
        return cls.SCHEDULE_TO_CLASS_STATUS_MAP.get(schedule_status, 4)

    @classmethod
    def make_class_no(cls):
        return f'CL{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def normalize_class_mode(cls, value):
        if value in ['oneToOne', 'one_to_one', '一对一']:
            return 'one_to_one'
        return 'group'

    @classmethod
    def to_decimal(cls, value, default=0):
        if value in [None, '']:
            return Decimal(str(default))
        return Decimal(str(value)).quantize(Decimal('0.01'))

    @classmethod
    def to_int(cls, value, default=0):
        if value in [None, '']:
            return default
        return int(value)

    @classmethod
    async def resolve_teacher(cls, query_db: AsyncSession, teacher_id: int | None):
        if not teacher_id:
            return None
        teacher = await TeachClassDao.get_teacher_by_id(query_db, teacher_id)
        if not teacher:
            raise ServiceException(message='班级老师不存在')
        return teacher

    @classmethod
    async def build_class_do(cls, query_db: AsyncSession, page_object: AddTeachClassModel, current_user_name: str):
        course = await TeachCourseDao.get_teach_course_by_id(query_db, page_object.course_id)
        if not course or course.status != 1:
            raise ServiceException(message='关联课程不存在或已停用')
        teacher = await cls.resolve_teacher(query_db, page_object.teacher_id)
        assistant = await cls.resolve_teacher(query_db, page_object.assistant_id)
        return TeachClass(
            class_no=page_object.class_no or cls.make_class_no(),
            class_name=page_object.class_name,
            class_mode=cls.normalize_class_mode(page_object.class_mode),
            class_type=page_object.class_type or 'custom',
            course_id=course.id,
            course_name=course.course_name,
            course_type=course.course_type,
            teacher_id=teacher.id if teacher else None,
            teacher_name=teacher.teacher_name if teacher else None,
            assistant_id=assistant.id if assistant else None,
            assistant_name=assistant.teacher_name if assistant else None,
            classroom=page_object.classroom,
            max_students=cls.to_int(page_object.max_students, 0),
            min_students=cls.to_int(page_object.min_students, 0),
            allow_over_capacity=cls.to_int(page_object.allow_over_capacity, 1),
            allow_online_enroll=cls.to_int(page_object.allow_online_enroll, 0),
            allow_recharge=cls.to_int(page_object.allow_recharge, 1),
            auto_assign_name=cls.to_int(page_object.auto_assign_name, 0),
            lesson_hours=cls.to_decimal(page_object.lesson_hours, 1),
            default_consumption=cls.to_decimal(page_object.default_consumption, 0),
            enroll_status=cls.to_int(page_object.enroll_status, 1),
            start_date=page_object.start_date,
            end_date=page_object.end_date,
            status=cls.to_int(page_object.status, 1),
            is_historical=cls.to_int(page_object.is_historical, 0),
            create_by=current_user_name,
            create_time=datetime.now(),
            update_by=current_user_name,
            update_time=datetime.now(),
            remark=page_object.remark,
        )

    @classmethod
    async def save_teacher_relations(cls, query_db: AsyncSession, class_obj: TeachClass, current_user_name: str):
        await TeachClassDao.delete_class_teachers(query_db, class_obj.id, current_user_name)
        if class_obj.teacher_id:
            await TeachClassDao.add_class_teacher(
                query_db,
                TeachClassTeacher(
                    class_id=class_obj.id,
                    teacher_id=class_obj.teacher_id,
                    teacher_name=class_obj.teacher_name,
                    teacher_role='main',
                    create_by=current_user_name,
                    update_by=current_user_name,
                ),
            )
        if class_obj.assistant_id:
            await TeachClassDao.add_class_teacher(
                query_db,
                TeachClassTeacher(
                    class_id=class_obj.id,
                    teacher_id=class_obj.assistant_id,
                    teacher_name=class_obj.assistant_name,
                    teacher_role='assistant',
                    create_by=current_user_name,
                    update_by=current_user_name,
                ),
            )

    @classmethod
    def format_class_row(cls, row: dict):
        class_mode = row.get('classMode') or row.get('class_mode')
        class_type = row.get('classType') or row.get('class_type')
        enroll_status = row.get('enrollStatus') if row.get('enrollStatus') is not None else row.get('enroll_status')
        row['classMode'] = class_mode
        row['classModeName'] = cls.CLASS_MODE_LABELS.get(class_mode, class_mode)
        row['classType'] = class_type
        row['classTypeName'] = cls.CLASS_TYPE_LABELS.get(class_type, class_type)
        row['enrollStatusName'] = cls.ENROLL_STATUS_LABELS.get(enroll_status, enroll_status)
        row['capacityText'] = f"{row.get('currentStudents') or 0}/{row.get('maxStudents') or '未设置'}"
        row['actualStudents'] = row.get('currentStudents') or 0
        row['capacity'] = row.get('maxStudents') or '未设置'
        row['lessonDuration'] = row.get('lessonHours') or 0
        return row

    @classmethod
    async def get_teach_class_list_services(
        cls, query_db: AsyncSession, query_object: TeachClassPageQueryModel, data_scope_sql: str, is_page: bool = True
    ):
        if query_object.class_mode:
            query_object.class_mode = cls.normalize_class_mode(query_object.class_mode)
        page_result = await TeachClassDao.get_teach_class_list(query_db, query_object, data_scope_sql, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = [cls.format_class_row(row) for row in page_result.rows]
            return page_result
        return [cls.format_class_row(row) for row in page_result]

    @classmethod
    async def get_teach_class_detail_services(cls, query_db: AsyncSession, class_id: int):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        return cls.format_class_row(CamelCaseUtil.transform_result(class_obj))

    @classmethod
    async def get_teach_class_options_services(
        cls, query_db: AsyncSession, course_id: int | None = None, keyword: str | None = None, class_mode: str | None = None
    ):
        query_object = TeachClassPageQueryModel(
            page_num=1,
            page_size=500,
            course_id=course_id,
            class_name=keyword,
            class_mode=class_mode,
            status=1,
        )
        rows = await cls.get_teach_class_list_services(query_db, query_object, data_scope_sql='', is_page=False)
        return [
            {
                'id': row.get('id'),
                'classNo': row.get('classNo'),
                'className': row.get('className'),
                'classMode': row.get('classMode'),
                'courseId': row.get('courseId'),
                'courseName': row.get('courseName'),
                'teacherId': row.get('teacherId'),
                'teacherName': row.get('teacherName'),
                'classroom': row.get('classroom'),
                'lessonHours': row.get('lessonHours'),
                'currentStudents': row.get('currentStudents') or 0,
                'maxStudents': row.get('maxStudents') or 0,
                'allowOverCapacity': row.get('allowOverCapacity') or 0,
                'enrollStatus': row.get('enrollStatus'),
                'disabled': row.get('enrollStatus') == 3,
            }
            for row in rows
        ]

    @classmethod
    async def add_teach_class_services(
        cls, query_db: AsyncSession, page_object: AddTeachClassModel, current_user_name: str
    ):
        if page_object.class_no:
            exist = await TeachClassDao.get_teach_class_by_no(query_db, page_object.class_no)
            if exist:
                raise ServiceException(message='班级编号已存在')
        try:
            class_obj = await cls.build_class_do(query_db, page_object, current_user_name)
            class_obj = await TeachClassDao.add_teach_class(query_db, class_obj)
            await cls.save_teacher_relations(query_db, class_obj, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': class_obj.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_class_services(
        cls, query_db: AsyncSession, page_object: EditTeachClassModel, current_user_name: str
    ):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, page_object.id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        if page_object.class_no:
            exist = await TeachClassDao.get_teach_class_by_no(query_db, page_object.class_no)
            if exist and exist.id != page_object.id:
                raise ServiceException(message='班级编号已存在')
        new_obj = await cls.build_class_do(query_db, page_object, current_user_name)
        try:
            class_obj.class_no = page_object.class_no or class_obj.class_no
            class_obj.class_name = new_obj.class_name
            class_obj.class_mode = new_obj.class_mode
            class_obj.class_type = new_obj.class_type
            class_obj.course_id = new_obj.course_id
            class_obj.course_name = new_obj.course_name
            class_obj.course_type = new_obj.course_type
            class_obj.teacher_id = new_obj.teacher_id
            class_obj.teacher_name = new_obj.teacher_name
            class_obj.assistant_id = new_obj.assistant_id
            class_obj.assistant_name = new_obj.assistant_name
            class_obj.classroom = new_obj.classroom
            class_obj.max_students = new_obj.max_students
            class_obj.min_students = new_obj.min_students
            class_obj.allow_over_capacity = new_obj.allow_over_capacity
            class_obj.allow_online_enroll = new_obj.allow_online_enroll
            class_obj.allow_recharge = new_obj.allow_recharge
            class_obj.auto_assign_name = new_obj.auto_assign_name
            class_obj.lesson_hours = new_obj.lesson_hours
            class_obj.default_consumption = new_obj.default_consumption
            class_obj.enroll_status = new_obj.enroll_status
            class_obj.start_date = new_obj.start_date
            class_obj.end_date = new_obj.end_date
            class_obj.status = new_obj.status
            class_obj.is_historical = new_obj.is_historical
            class_obj.remark = new_obj.remark
            class_obj.update_by = current_user_name
            await TeachClassDao.edit_teach_class(query_db, class_obj)
            await cls.save_teacher_relations(query_db, class_obj, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_class_services(
        cls, query_db: AsyncSession, page_object: DeleteTeachClassModel, current_user_name: str
    ):
        class_ids = [int(item) for item in page_object.class_ids.split(',') if item.strip()]
        if not class_ids:
            raise ServiceException(message='请选择要删除的班级')
        try:
            await TeachClassDao.delete_teach_class(query_db, class_ids, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def change_recharge_services(
        cls, query_db: AsyncSession, page_object: ChangeTeachClassRechargeModel, current_user_name: str
    ):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, page_object.id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        try:
            await TeachClassDao.update_teach_class_recharge(
                query_db, page_object.id, page_object.allow_recharge, current_user_name
            )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='状态修改成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    def format_class_student_row(cls, class_student, student, base_user, course_account=None):
        row = CamelCaseUtil.transform_result(class_student)
        row['studentName'] = student.student_name
        row['gender'] = student.gender
        row['genderName'] = cls.GENDER_LABELS.get(student.gender, '未知')
        row['phone'] = base_user.phone
        row['courseName'] = course_account.course_name if course_account else None
        row['consumeMethod'] = (
            class_student.consume_method
            or (f'{course_account.course_name}({course_account.remaining_quantity}{course_account.unit or ""})' if course_account else '未绑定课程账户')
        )
        row['remainingQuantity'] = course_account.remaining_quantity if course_account else None
        row['remainingType'] = course_account.unit if course_account else None
        row['statusName'] = '在读' if row.get('status') == 1 else '已移出'
        return row

    @classmethod
    async def get_class_students_services(cls, query_db: AsyncSession, class_id: int):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        rows = await TeachClassDao.get_class_students(query_db, class_id)
        return [cls.format_class_student_row(*row) for row in rows]

    @classmethod
    async def get_available_students_services(cls, query_db: AsyncSession, class_id: int, keyword: str | None = None):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        rows = await TeachClassDao.get_available_students(query_db, class_obj, keyword)
        result = []
        for student, base_user, course_account in rows:
            result.append(
                {
                    'id': student.id,
                    'studentName': student.student_name,
                    'gender': student.gender,
                    'genderName': cls.GENDER_LABELS.get(student.gender, '未知'),
                    'phone': base_user.phone,
                    'courseAccountId': course_account.id if course_account else None,
                    'courseName': course_account.course_name if course_account else class_obj.course_name,
                    'consumeMethod': (
                        f'{course_account.course_name}({course_account.remaining_quantity}{course_account.unit or ""})'
                        if course_account
                        else '未报名该课程'
                    ),
                    'remainingQuantity': course_account.remaining_quantity if course_account else None,
                }
            )
        return result

    @classmethod
    async def ensure_student_in_class(
        cls,
        query_db: AsyncSession,
        class_obj: TeachClass,
        student_id: int,
        current_user_name: str,
        course_account: TeachStudentCourseAccount | None = None,
        order_item: TeachEnrollmentOrderItem | None = None,
        remark: str | None = None,
    ):
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, student_id)
        if not student_result:
            raise ServiceException(message='学员不存在')
        student, _, _ = student_result
        existing = await TeachClassDao.get_class_student_any(query_db, class_obj.id, student.id)
        consume_method = (
            f'{course_account.course_name}({course_account.remaining_quantity}{course_account.unit or ""})'
            if course_account
            else None
        )
        if existing:
            existing.status = 1
            existing.del_flag = 0
            existing.leave_date = None
            existing.student_name = student.student_name
            existing.course_account_id = course_account.id if course_account else existing.course_account_id
            existing.enrollment_order_id = course_account.order_id if course_account else existing.enrollment_order_id
            existing.enrollment_order_item_id = (
                order_item.id if order_item else existing.enrollment_order_item_id
            )
            existing.consume_method = consume_method or existing.consume_method
            existing.remark = remark or existing.remark
            existing.update_by = current_user_name
            await TeachClassDao.edit_class_student(query_db, existing)
            return existing
        return await TeachClassDao.add_class_student(
            query_db,
            TeachClassStudent(
                class_id=class_obj.id,
                student_id=student.id,
                student_name=student.student_name,
                course_account_id=course_account.id if course_account else None,
                enrollment_order_id=course_account.order_id if course_account else None,
                enrollment_order_item_id=order_item.id if order_item else None,
                consume_method=consume_method,
                join_date=date.today(),
                status=1,
                create_by=current_user_name,
                create_time=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now(),
                remark=remark,
            ),
        )

    @classmethod
    async def add_class_students_services(
        cls, query_db: AsyncSession, class_id: int, page_object: AddTeachClassStudentModel, current_user_name: str
    ):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        active_count = class_obj.current_students or 0
        add_count = len(set(page_object.student_ids))
        if (
            class_obj.max_students
            and class_obj.allow_over_capacity != 1
            and active_count + add_count > class_obj.max_students
        ):
            raise ServiceException(message='班级容量不足，不能继续添加学员')
        try:
            for student_id in sorted(set(page_object.student_ids)):
                account = await TeachClassDao.get_student_course_account(query_db, student_id, class_obj.course_id)
                await cls.ensure_student_in_class(
                    query_db, class_obj, student_id, current_user_name, account, remark=page_object.remark
                )
                if account and not account.class_id:
                    account.class_id = class_obj.id
                    account.class_name = class_obj.class_name
                    account.update_by = current_user_name
            current_students = await TeachClassDao.refresh_class_student_count(query_db, class_obj.id)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'添加成功，共添加{current_students}名在读学员', result={'currentStudents': current_students}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def add_student_from_enrollment_services(
        cls,
        query_db: AsyncSession,
        class_id: int,
        student_id: int,
        course_account: TeachStudentCourseAccount,
        order_item: TeachEnrollmentOrderItem,
        current_user_name: str,
    ):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='报名选择的班级不存在')
        if class_obj.status != 1 or class_obj.enroll_status == 3:
            raise ServiceException(message='报名选择的班级不可招生')
        if class_obj.course_id != course_account.course_id:
            raise ServiceException(message='报名选择的班级与课程不匹配')
        if class_obj.max_students and class_obj.allow_over_capacity != 1 and (class_obj.current_students or 0) >= class_obj.max_students:
            raise ServiceException(message=f'班级({class_obj.class_name})已满员')
        await cls.ensure_student_in_class(query_db, class_obj, student_id, current_user_name, course_account, order_item)
        await TeachClassDao.refresh_class_student_count(query_db, class_obj.id)

    @classmethod
    async def remove_class_students_services(
        cls, query_db: AsyncSession, class_id: int, page_object: RemoveTeachClassStudentModel, current_user_name: str
    ):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        student_ids = [int(item) for item in page_object.student_ids.split(',') if item.strip()]
        if not student_ids:
            raise ServiceException(message='请选择要移出的学员')
        try:
            await TeachClassDao.remove_class_students(query_db, class_id, student_ids, current_user_name)
            current_students = await TeachClassDao.refresh_class_student_count(query_db, class_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='移出成功', result={'currentStudents': current_students})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_attendance_prepare_services(cls, query_db: AsyncSession, class_id: int, event_id: int | None = None):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        students = await cls.get_class_students_services(query_db, class_id)
        event = None
        event_teacher = None
        schedule_attendance_map = {}
        if event_id:
            event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, event_id)
            if not event:
                raise ServiceException(message='排课课次不存在')
            if event.class_id != class_id:
                raise ServiceException(message='排课课次不属于当前班级')
            if await TeachClassDao.get_class_attendance_by_event_id(query_db, event_id):
                raise ServiceException(message='该课次已完成点名')
            event_teacher = await cls.resolve_teacher(query_db, event.teacher_id) if event.teacher_id else None
            schedule_attendances = await TeachScheduleAttendanceDao.get_attendances_by_event(query_db, event_id)
            schedule_attendance_map = {item.student_id: item for item in schedule_attendances}

        default_start_time = '09:00'
        default_end_time = '10:00'
        start_time = event.start_time.strftime('%H:%M') if event else default_start_time
        end_time = event.end_time.strftime('%H:%M') if event else default_end_time
        prepared_students = []
        for student in students:
            schedule_attendance = schedule_attendance_map.get(student.get('studentId'))
            if event_id and not schedule_attendance:
                continue
            # schedule_attendance.status 来自旧表(0未到 1出勤 2迟到 3请假 4缺勤),
            # 需先反向映射成新表枚举, 否则旧表的 0未到 会被新表标签字典显示成"到课"。
            raw_schedule_status = schedule_attendance.status if schedule_attendance else None
            attendance_status = (
                cls.map_schedule_status_to_class(raw_schedule_status)
                if raw_schedule_status is not None
                else 1
            )
            prepared_students.append(
                {
                    **student,
                    'attendanceStatus': attendance_status,
                    'attendanceStatusName': cls.ATTENDANCE_STATUS_LABELS.get(attendance_status, '到课'),
                    'deductQuantity': 1
                    if attendance_status in [1, 2]
                    and student.get('courseAccountId')
                    and (student.get('remainingQuantity') or 0) > 0
                    else 0,
                    'remark': schedule_attendance.notes if schedule_attendance else '',
                }
            )

        return {
            'classInfo': cls.format_class_row(CamelCaseUtil.transform_result(class_obj)),
            'form': {
                'eventId': event_id,
                'classDate': event.event_date if event else date.today(),
                'startTime': start_time,
                'endTime': end_time,
                'teacherId': event.teacher_id if event else class_obj.teacher_id,
                'teacherName': event_teacher.teacher_name if event_teacher else class_obj.teacher_name,
                'courseId': event.course_id if event else class_obj.course_id,
                'courseName': event.course_name if event else class_obj.course_name,
                'classroom': event.classroom if event else class_obj.classroom,
                'lessonHours': event.lesson_hours if event else class_obj.lesson_hours or Decimal('1'),
                'content': event.content if event else '',
            },
            'students': prepared_students,
        }

    @classmethod
    def format_attendance_row(cls, attendance: TeachClassAttendance):
        row = CamelCaseUtil.transform_result(attendance)
        row['attendanceTime'] = attendance.create_time
        row['expectedCount'] = attendance.student_count
        row['actualCount'] = (attendance.present_count or 0) + (attendance.late_count or 0)
        row['duration'] = attendance.lesson_hours
        row['statusName'] = '已点名'
        return row

    @classmethod
    async def get_class_attendance_list_services(cls, query_db: AsyncSession, class_id: int):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        rows = await TeachClassDao.get_class_attendance_list(query_db, class_id)
        return [cls.format_attendance_row(row) for row in rows]

    @classmethod
    async def get_class_attendance_detail_services(cls, query_db: AsyncSession, attendance_id: int):
        rows = await TeachClassDao.get_class_attendance_detail(query_db, attendance_id)
        if not rows:
            raise ServiceException(message='点名记录不存在')
        attendance = rows[0][0]
        details = []
        for _, detail, student, base_user in rows:
            detail_row = CamelCaseUtil.transform_result(detail)
            detail_row['studentName'] = student.student_name
            detail_row['phone'] = base_user.phone
            detail_row['statusName'] = cls.ATTENDANCE_STATUS_LABELS.get(detail.status, '-')
            details.append(detail_row)
        return {
            **cls.format_attendance_row(attendance),
            'details': details,
        }

    @classmethod
    async def submit_class_attendance_services(
        cls,
        query_db: AsyncSession,
        class_id: int,
        page_object: SubmitTeachClassAttendanceModel,
        current_user_name: str,
    ):
        # 锁定班级行，串行化同一班级的点名提交，防止并发重复扣课和完成课次丢失更新
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id, for_update=True)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        event = None
        schedule_attendance_map = {}
        if page_object.event_id:
            event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, page_object.event_id)
            if not event:
                raise ServiceException(message='排课课次不存在')
            if event.class_id != class_id:
                raise ServiceException(message='排课课次不属于当前班级')
            if event.status == '3':
                raise ServiceException(message='已取消课次不能点名')
            if await TeachClassDao.get_class_attendance_by_event_id(query_db, page_object.event_id, for_update=True):
                raise ServiceException(message='该课次已完成点名')
            schedule_attendances = await TeachScheduleAttendanceDao.get_attendances_by_event(
                query_db, page_object.event_id
            )
            schedule_attendance_map = {item.student_id: item for item in schedule_attendances}
        teacher = await cls.resolve_teacher(query_db, page_object.teacher_id) if page_object.teacher_id else None
        member_rows = await TeachClassDao.get_class_students(query_db, class_id)
        member_map = {class_student.student_id: (class_student, student, base_user, account) for class_student, student, base_user, account in member_rows}
        detail_items = page_object.details
        status_count = {1: 0, 2: 0, 3: 0, 4: 0}
        deduct_total = 0
        try:
            for item in detail_items:
                if item.student_id not in member_map:
                    raise ServiceException(message='点名学员不属于当前班级')
                if page_object.event_id and item.student_id not in schedule_attendance_map:
                    raise ServiceException(message='点名学员不在该课次名单中')
                if item.status not in cls.ATTENDANCE_STATUS_LABELS:
                    raise ServiceException(message='到课状态不正确')
                deduct_quantity = max(cls.to_int(item.deduct_quantity, 0), 0)
                if item.status in [3, 4]:
                    deduct_quantity = 0
                class_student, _, _, account = member_map[item.student_id]
                if deduct_quantity > 0:
                    account = account or (
                        await TeachClassDao.get_course_account_by_id(query_db, class_student.course_account_id)
                        if class_student.course_account_id
                        else None
                    )
                    if not account:
                        raise ServiceException(message=f'{class_student.student_name}未绑定课程账户，不能扣课')
                    if (account.remaining_quantity or 0) < deduct_quantity:
                        raise ServiceException(message=f'{class_student.student_name}剩余课时不足')
                status_count[item.status] += 1
                deduct_total += deduct_quantity

            attendance = await TeachClassDao.add_class_attendance(
                query_db,
                TeachClassAttendance(
                    event_id=page_object.event_id,
                    class_id=class_obj.id,
                    class_name=class_obj.class_name,
                    course_id=(event.course_id if event else class_obj.course_id) or class_obj.course_id,
                    course_name=(event.course_name if event else class_obj.course_name) or class_obj.course_name,
                    teacher_id=teacher.id if teacher else class_obj.teacher_id,
                    teacher_name=teacher.teacher_name if teacher else class_obj.teacher_name,
                    classroom=page_object.classroom or (event.classroom if event else class_obj.classroom),
                    class_date=page_object.class_date,
                    start_time=page_object.start_time,
                    end_time=page_object.end_time,
                    lesson_hours=cls.to_decimal(page_object.lesson_hours, 1),
                    content=page_object.content,
                    student_count=len(detail_items),
                    present_count=status_count[1],
                    late_count=status_count[2],
                    leave_count=status_count[3],
                    absent_count=status_count[4],
                    deducted_quantity=deduct_total,
                    create_by=current_user_name,
                    create_time=datetime.now(),
                    update_by=current_user_name,
                    update_time=datetime.now(),
                    remark=page_object.remark,
                ),
            )
            for item in detail_items:
                class_student, student, _, account = member_map[item.student_id]
                deduct_quantity = max(cls.to_int(item.deduct_quantity, 0), 0)
                if item.status in [3, 4]:
                    deduct_quantity = 0
                if deduct_quantity > 0:
                    # 扣课前加锁重新读取课程账户，防止同一账户被并发扣减
                    account = await TeachClassDao.get_course_account_by_id(
                        query_db, account.id if account else class_student.course_account_id, for_update=True
                    )
                    if not account or (account.remaining_quantity or 0) < deduct_quantity:
                        raise ServiceException(message=f'{class_student.student_name}剩余课时不足')
                    before_remaining = account.remaining_quantity or 0
                    account.consumed_quantity = (account.consumed_quantity or 0) + deduct_quantity
                    account.remaining_quantity = before_remaining - deduct_quantity
                    account.update_by = current_user_name
                    account.update_time = datetime.now()
                    after_remaining = account.remaining_quantity
                else:
                    before_remaining = account.remaining_quantity if account else None
                    after_remaining = before_remaining
                await TeachClassDao.add_class_attendance_detail(
                    query_db,
                    TeachClassAttendanceDetail(
                        attendance_id=attendance.id,
                        class_id=class_obj.id,
                        student_id=student.id,
                        student_name=student.student_name,
                        course_account_id=account.id if account else class_student.course_account_id,
                        status=item.status,
                        deduct_quantity=deduct_quantity,
                        before_remaining=before_remaining,
                        after_remaining=after_remaining,
                        consume_method=class_student.consume_method,
                        create_by=current_user_name,
                        create_time=datetime.now(),
                        update_by=current_user_name,
                        update_time=datetime.now(),
                        remark=item.remark,
                    ),
                )
                if page_object.event_id:
                    schedule_attendance = schedule_attendance_map[item.student_id]
                    # 新表枚举与旧表枚举不同, 必须显式映射后再反写, 避免跨表串味
                    schedule_attendance.status = cls.map_class_status_to_schedule(item.status)
                    schedule_attendance.check_in_time = datetime.now()
                    schedule_attendance.check_in_method = 'M'
                    schedule_attendance.notes = item.remark
                    schedule_attendance.update_by = current_user_name
                    schedule_attendance.update_time = datetime.now()
            class_obj.completed_lessons = (class_obj.completed_lessons or 0) + 1
            class_obj.completed_hours = cls.to_decimal((class_obj.completed_hours or 0) + cls.to_decimal(page_object.lesson_hours, 1), 0)
            class_obj.update_by = current_user_name
            class_obj.update_time = datetime.now()
            if event:
                planned = len(detail_items)
                event.status = '2'
                event.cached_planned = planned
                event.cached_present = status_count[1]
                event.cached_late = status_count[2]
                event.cached_excused = status_count[3]
                event.cached_absent = status_count[4]
                event.cached_rate = round((status_count[1] + status_count[2]) / planned * 100, 2) if planned else 0
                event.update_by = current_user_name
                event.update_time = datetime.now()
            attendance_id = attendance.id
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='点名完成', result={'id': attendance_id})
        except IntegrityError as e:
            await query_db.rollback()
            # uk_class_attendance_event 唯一约束兜底：同一课次并发重复提交
            if page_object.event_id:
                raise ServiceException(message='该课次已完成点名') from e
            raise e
        except Exception as e:
            await query_db.rollback()
            raise e
