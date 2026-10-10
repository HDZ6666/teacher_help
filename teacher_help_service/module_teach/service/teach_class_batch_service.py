from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_student_account_dao import TeachStudentAccountDao
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.do.teach_class_do import TeachClass, TeachClassStudent
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from module_teach.entity.vo.teach_class_vo import AddTeachClassModel
from module_teach.entity.vo.teach_student_account_vo import ClassBatchIdsModel, ClassPromoteModel
from module_teach.service.teach_class_service import TeachClassService
from module_teach.service.teach_import_util import ImportRowError, TeachImportUtil


class TeachClassBatchService:
    """
    班级批量操作（P3）：导入班级、批量升班、批量结业
    """

    IMPORT_HEADERS = [
        '*班级名称',
        '*关联课程',
        '班级容量',
        '*班级超额',
        '开课人数',
        '上课教室',
        '班级老师',
        '默认授课课时',
        '备注',
    ]
    IMPORT_NOTES = [
        '1. 请勿修改表头和列顺序，带 * 的列为必填；第2行为示例，导入前请删除。',
        '2. 关联课程须与系统中启用的课程名称完全一致（当前一个班级只能关联一门课程）。',
        '3. 班级超额填写“可超额/不可超额”；选择“不可超额”时班级容量必填且大于0。',
        '4. 班级老师填写老师姓名，若有重名请写成“姓名(手机号)”；不填则不设置老师。',
        '5. 班级名称不能与已有班级重复；整表先校验，任何一行有错误都不会导入。',
        '6. 默认授课课时不填为1。单次最多 2000 行。',
    ]

    # ------------------------------------------------------------------ 导入班级

    @classmethod
    async def get_import_template_services(cls, query_db: AsyncSession):
        courses = (
            (
                await query_db.execute(
                    select(TeachCourse.course_name)
                    .where(TeachCourse.del_flag == 0, TeachCourse.status == 1)
                    .order_by(TeachCourse.course_name)
                    .limit(500)
                )
            )
            .scalars()
            .all()
        )
        return TeachImportUtil.build_template(
            '班级导入',
            cls.IMPORT_HEADERS,
            cls.IMPORT_NOTES,
            options={'*关联课程': list(courses), '*班级超额': ['可超额', '不可超额']},
            example=['数学启蒙一班', courses[0] if courses else '数学启蒙', 20, '可超额', '', '1号教室', '', 1, ''],
        )

    @classmethod
    async def find_teacher(cls, query_db: AsyncSession, text: str | None):
        if not text:
            return None
        name, phone = text, None
        for left, right in (('(', ')'), ('（', '）')):
            if left in text and text.endswith(right):
                name, phone = text[: text.index(left)].strip(), text[text.index(left) + 1 : -1].strip()
                break
        query = (
            select(TeachTeacher, TeachBaseUser.phone)
            .outerjoin(TeachBaseUser, TeachBaseUser.id == TeachTeacher.user_id)
            .where(TeachTeacher.teacher_name == name, TeachTeacher.del_flag == '0')
        )
        rows = (await query_db.execute(query)).all()
        if phone:
            rows = [row for row in rows if row[1] == phone]
        if not rows:
            raise ImportRowError(f'班级老师“{text}”不存在')
        if len(rows) > 1:
            raise ImportRowError(f'班级老师“{name}”有重名，请写成“姓名(手机号)”')
        return rows[0][0]

    @classmethod
    async def validate_import_row(cls, query_db: AsyncSession, values: dict, names: dict, line: int):
        class_name = TeachImportUtil.required(values, '班级名称')
        if len(class_name) > 100:
            raise ImportRowError('班级名称不能超过100字')
        if class_name in names:
            raise ImportRowError(f'班级名称与第{names[class_name]}行重复')
        names[class_name] = line
        exists = (
            await query_db.execute(
                select(func.count(TeachClass.id)).where(TeachClass.class_name == class_name, TeachClass.del_flag == 0)
            )
        ).scalar()
        if exists:
            raise ImportRowError(f'班级“{class_name}”已存在')
        course_name = TeachImportUtil.required(values, '关联课程')
        courses = (
            (
                await query_db.execute(
                    select(TeachCourse).where(
                        TeachCourse.course_name == course_name, TeachCourse.del_flag == 0, TeachCourse.status == 1
                    )
                )
            )
            .scalars()
            .all()
        )
        if not courses:
            raise ImportRowError(f'课程“{course_name}”不存在或已停用')
        if len(courses) > 1:
            raise ImportRowError(f'课程“{course_name}”存在重名')
        over_text = TeachImportUtil.required(values, '班级超额')
        if over_text not in ('可超额', '不可超额'):
            raise ImportRowError('班级超额只能填写“可超额”或“不可超额”')
        max_students = TeachImportUtil.parse_int(values, '班级容量')
        if over_text == '不可超额' and max_students <= 0:
            raise ImportRowError('选择“不可超额”时班级容量必填且大于0')
        teacher = await cls.find_teacher(query_db, values.get('班级老师'))
        return AddTeachClassModel(
            className=class_name,
            classMode='group',
            courseId=courses[0].id,
            teacherId=teacher.id if teacher else None,
            classroom=(values.get('上课教室') or '')[:100] or None,
            maxStudents=max_students,
            minStudents=TeachImportUtil.parse_int(values, '开课人数'),
            allowOverCapacity=1 if over_text == '可超额' else 0,
            lessonHours=TeachImportUtil.parse_decimal(values, '默认授课课时', Decimal('1')),
            remark=(values.get('备注') or '')[:500] or None,
        )

    @classmethod
    async def import_services(cls, query_db: AsyncSession, file, current_user_name: str):
        required = [header.lstrip('*') for header in cls.IMPORT_HEADERS if header.startswith('*')]
        rows = await TeachImportUtil.read_rows(file, required)
        errors, models, names = [], [], {}
        for line, values in rows:
            try:
                models.append(await cls.validate_import_row(query_db, values, names, line))
            except ImportRowError as e:
                errors.append({'row': line, 'message': str(e)})
            except ValueError as e:
                errors.append({'row': line, 'message': f'数据格式不正确：{e}'})
        if errors:
            return TeachImportUtil.result(len(rows), errors)
        try:
            for model in models:
                class_obj = await TeachClassService.build_class_do(query_db, model, current_user_name)
                class_obj = await TeachClassDao.add_teach_class(query_db, class_obj)
                await TeachClassService.save_teacher_relations(query_db, class_obj, current_user_name)
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise e
        return TeachImportUtil.result(len(rows), [], len(models))

    # ------------------------------------------------------------------ 批量结业

    @classmethod
    async def count_future_events(cls, query_db: AsyncSession, class_id: int, from_date: date):
        return (
            await query_db.execute(
                select(func.count(TeachScheduleEvent.id)).where(
                    TeachScheduleEvent.class_id == class_id,
                    TeachScheduleEvent.del_flag == '0',
                    TeachScheduleEvent.status.in_(['0', '1']),
                    TeachScheduleEvent.event_date > from_date,
                )
            )
        ).scalar() or 0

    @classmethod
    async def active_members(cls, query_db: AsyncSession, class_id: int):
        return (
            (
                await query_db.execute(
                    select(TeachClassStudent).where(
                        TeachClassStudent.class_id == class_id,
                        TeachClassStudent.status == 1,
                        TeachClassStudent.del_flag == 0,
                    )
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def graduate_services(cls, query_db: AsyncSession, page_object: ClassBatchIdsModel, current_user_name: str):
        """
        批量结业：班级招生状态置为“已结课”、在读学员全部移出（课程账户与剩余课时不变）。
        已排但未上的课次不自动删除，只在结果中提示数量。
        """
        end_date = page_object.end_date or date.today()
        try:
            summary = []
            for class_id in sorted(set(page_object.class_ids)):
                class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id, for_update=True)
                if not class_obj:
                    raise ServiceException(message='部分班级不存在或已删除，请刷新后重试')
                if class_obj.enroll_status == 3:
                    raise ServiceException(message=f'班级（{class_obj.class_name}）已结业')
                members = await cls.active_members(query_db, class_id)
                if members:
                    await TeachClassDao.remove_class_students(
                        query_db, class_id, [member.student_id for member in members], current_user_name
                    )
                await TeachClassDao.refresh_class_student_count(query_db, class_id)
                await TeachStudentAccountDao.set_class_enroll_status(query_db, class_id, 3)
                class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id, for_update=True)
                class_obj.end_date = class_obj.end_date or end_date
                class_obj.update_by = current_user_name
                class_obj.update_time = datetime.now()
                summary.append(
                    {
                        'classId': class_id,
                        'className': class_obj.class_name,
                        'removedStudents': len(members),
                        'futureEvents': await cls.count_future_events(query_db, class_id, end_date),
                    }
                )
            await query_db.commit()
            future = sum(item['futureEvents'] for item in summary)
            message = f'已结业{len(summary)}个班级'
            if future:
                message += f'，仍有{future}个未上课次未删除，请到课表中处理'
            return CrudResponseModel(is_success=True, message=message, result=summary)
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 批量升班

    @classmethod
    async def promote_services(cls, query_db: AsyncSession, page_object: ClassPromoteModel, current_user_name: str):
        """
        批量升班：按原班级创建新班级并把学员转入新班；原班级学员移出。
        新班级课程与原班级相同则沿用学员原课程账户；不同则绑定学员在新课程下的有效账户，没有则不绑定（点名不能扣课），在结果中列出。
        不复制原班级排课；graduate_source=true 时原班级同时置为“已结课”。
        """
        source_ids = [item.source_class_id for item in page_object.items]
        if len(set(source_ids)) != len(source_ids):
            raise ServiceException(message='同一个原班级只能升班一次')
        new_names = [item.class_name for item in page_object.items]
        if len(set(new_names)) != len(new_names):
            raise ServiceException(message='新班级名称不能重复')
        try:
            summary = []
            for item in sorted(page_object.items, key=lambda x: x.source_class_id):
                source = await TeachClassDao.get_teach_class_by_id(query_db, item.source_class_id, for_update=True)
                if not source:
                    raise ServiceException(message='原班级不存在或已删除')
                exists = (
                    await query_db.execute(
                        select(func.count(TeachClass.id)).where(
                            TeachClass.class_name == item.class_name, TeachClass.del_flag == 0
                        )
                    )
                ).scalar()
                if exists:
                    raise ServiceException(message=f'班级“{item.class_name}”已存在')
                members = await cls.active_members(query_db, source.id)
                member_map = {member.student_id: member for member in members}
                student_ids = item.student_ids if item.student_ids is not None else list(member_map)
                not_in_class = [sid for sid in student_ids if sid not in member_map]
                if not_in_class:
                    raise ServiceException(message=f'部分升班学员不在原班级（{source.class_name}）中')
                if not student_ids:
                    raise ServiceException(message=f'原班级（{source.class_name}）没有可升班的在读学员')
                course_id = item.course_id or source.course_id
                course = await TeachCourseDao.get_teach_course_by_id(query_db, course_id)
                if not course or course.status != 1:
                    raise ServiceException(message='新班级关联课程不存在或已停用')
                model = AddTeachClassModel(
                    className=item.class_name,
                    classMode=source.class_mode,
                    courseId=course_id,
                    teacherId=item.teacher_id or source.teacher_id,
                    assistantId=source.assistant_id,
                    classroom=item.classroom if item.classroom is not None else source.classroom,
                    maxStudents=item.max_students if item.max_students is not None else source.max_students,
                    minStudents=source.min_students,
                    allowOverCapacity=source.allow_over_capacity,
                    allowRecharge=source.allow_recharge,
                    lessonHours=Decimal(str(item.lesson_hours)) if item.lesson_hours else source.lesson_hours,
                    defaultConsumption=source.default_consumption,
                    startDate=item.start_date,
                    remark=f'由班级“{source.class_name}”升班',
                )
                new_class = await TeachClassService.build_class_do(query_db, model, current_user_name)
                if (
                    new_class.max_students
                    and new_class.allow_over_capacity != 1
                    and len(student_ids) > new_class.max_students
                ):
                    raise ServiceException(
                        message=f'新班级“{item.class_name}”容量不足以容纳{len(student_ids)}名升班学员'
                    )
                new_class = await TeachClassDao.add_teach_class(query_db, new_class)
                await TeachClassService.save_teacher_relations(query_db, new_class, current_user_name)
                unbound = []
                for student_id in sorted(student_ids):
                    member = member_map[student_id]
                    account = None
                    if course_id == source.course_id and member.course_account_id:
                        account = await TeachClassDao.get_course_account_by_id(query_db, member.course_account_id)
                        account = account if account and account.status == 'active' else None
                    if not account:
                        account = await TeachClassDao.get_student_course_account(query_db, student_id, course_id)
                    if not account:
                        unbound.append(member.student_name)
                    await TeachClassService.ensure_student_in_class(
                        query_db,
                        new_class,
                        student_id,
                        current_user_name,
                        account,
                        remark=f'由班级“{source.class_name}”升班',
                    )
                    if account and account.class_id in (None, source.id):
                        account.class_id = new_class.id
                        account.class_name = new_class.class_name
                        account.update_by = current_user_name
                await TeachClassDao.remove_class_students(query_db, source.id, sorted(student_ids), current_user_name)
                await TeachClassDao.refresh_class_student_count(query_db, source.id)
                await TeachClassDao.refresh_class_student_count(query_db, new_class.id)
                if page_object.graduate_source:
                    await TeachStudentAccountDao.set_class_enroll_status(query_db, source.id, 3)
                summary.append(
                    {
                        'sourceClassId': source.id,
                        'sourceClassName': source.class_name,
                        'newClassId': new_class.id,
                        'newClassName': new_class.class_name,
                        'promotedStudents': len(student_ids),
                        'unboundStudents': unbound,
                    }
                )
            await query_db.commit()
            unbound_total = sum(len(item['unboundStudents']) for item in summary)
            message = f'升班成功，共创建{len(summary)}个新班级'
            if unbound_total:
                message += f'，其中{unbound_total}名学员在新课程下没有有效课程账户，点名前请先报读'
            return CrudResponseModel(is_success=True, message=message, result=summary)
        except Exception as e:
            await query_db.rollback()
            raise e
