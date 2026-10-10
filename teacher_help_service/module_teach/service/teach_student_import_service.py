import secrets
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.do.user_do import SysUser
from module_teach.dao.teach_enrollment_dao import TeachEnrollmentDao
from module_teach.dao.teach_student_account_dao import TeachStudentAccountDao
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.do.teach_class_do import TeachClass
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_course_price_do import TeachCoursePrice
from module_teach.entity.do.teach_enrollment_order_do import (
    TeachCourseAccountLog,
    TeachEnrollmentOrder,
    TeachEnrollmentOrderItem,
    TeachStudentCourseAccount,
)
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.service.teach_class_service import TeachClassService
from module_teach.service.teach_import_util import ImportRowError, TeachImportUtil
from utils.pwd_util import PwdUtil


class TeachStudentImportService:
    """
    学员导入（P3）：学生基本信息 / 按课时报读 / 按月报读 三个模板

    规则（保守默认，见 doc/P3修复记录）：
    1. 先整表校验，任一行有错则整批不导入，返回错误行；全部通过才在一个事务中写入。
    2. 手机号对应家长不存在时自动创建家长账号（随机初始密码，家长需走找回密码）；学员按“家长手机号+姓名”识别。
    3. 学生基本信息导入遇到已存在学员报错，不覆盖；报读导入每行生成一张“导入”订单与一个课程账户（重复导入会重复生成）。
    """

    PAYMENT_METHODS = ['现金', '微信', '支付宝', '网银转账', 'POS机刷卡', '其他']
    GENDER_MAP = {'男': '1', '女': '2', '未知': '0'}
    STUDENT_HEADERS = [
        '*手机号',
        '*姓名',
        '性别',
        '出生日期',
        '就读学校',
        '当前年级',
        '家长姓名',
        '跟进人',
        '学管师',
        '备注',
    ]
    LESSON_HEADERS = [
        '*手机号',
        '*姓名',
        '性别',
        '*课程名称',
        '班级名称',
        '*购买课时',
        '*赠送课时',
        '*已上课时',
        '请假免扣剩余次数',
        '*应收金额（元）',
        '*实收金额（元）',
        '支付方式',
        '经办日期',
        '课程到期日期',
        '业绩归属人',
        '备注',
    ]
    MONTH_HEADERS = [
        '*手机号',
        '*姓名',
        '性别',
        '*课程名称',
        '班级名称',
        '*课程开始日期',
        '*课程结束日期',
        '赠送课程日期至',
        '*应收金额（元）',
        '*实收金额（元）',
        '支付方式',
        '经办日期',
        '业绩归属人',
        '备注',
    ]
    KINDS = {
        'student': ('学生基本信息', STUDENT_HEADERS),
        'lesson': ('按课时报读', LESSON_HEADERS),
        'month': ('按月报读', MONTH_HEADERS),
    }
    COMMON_NOTES = [
        '1. 请勿修改表头和列顺序，带 * 的列为必填；第2行为示例，导入前请删除。',
        '2. 手机号为家长登录家长端的唯一账号（11位）；该手机号还没有家长账号时会自动创建，'
        '初始密码随机，家长需通过找回密码设置。',
        '3. 系统按“手机号+学员姓名”识别学员；整表先校验，任何一行有错误都不会导入，请按错误提示修改后重新上传。',
        '4. 单次最多 2000 行，文件不超过 5MB。',
    ]
    KIND_NOTES = {
        'student': [
            '5. 学员已存在时报错，不会覆盖已有资料；性别填 男/女/未知；出生日期格式 YYYY-MM-DD。',
            '6. 跟进人/学管师填写系统员工的“用户昵称”（系统管理-用户管理），须唯一且为正常状态；不填为待分配。',
        ],
        'lesson': [
            '5. 课程名称须与系统中启用的课程完全一致，且课程设置了“按课时”收费；班级名称非必填，须属于该课程且可招生。',
            '6. 购买/赠送/已上课时须为大于等于0的整数，已上课时不能超过购买+赠送；剩余=购买+赠送-已上。',
            '7. 学员不存在时会按手机号+姓名自动建档；每行生成一张“导入”订单和一个课程账户，重复导入会重复生成。',
            '8. 应收>实收即为欠费；支付方式不填默认为现金；经办日期不填默认为导入当天。',
        ],
        'month': [
            '5. 课程名称须与系统中启用的课程完全一致，且课程设置了“按月”收费；班级名称非必填，须属于该课程且可招生。',
            '6. 购买月数按“课程开始日期~课程结束日期”的自然月计算（不足一月按一月），'
            '赠送月数按“课程结束日期~赠送课程日期至”计算；'
            '课程有效期为开始日期~（赠送日期至 或 结束日期）。',
            '7. 学员不存在时会按手机号+姓名自动建档；每行生成一张“导入”订单和一个课程账户，重复导入会重复生成。',
            '8. 应收>实收即为欠费；支付方式不填默认为现金；经办日期不填默认为导入当天。',
        ],
    }

    @classmethod
    def get_kind(cls, kind: str):
        if kind not in cls.KINDS:
            raise ServiceException(message='导入类型不正确')
        return cls.KINDS[kind]

    @classmethod
    async def get_template_services(cls, query_db: AsyncSession, kind: str):
        sheet_name, headers = cls.get_kind(kind)
        options = {'性别': ['男', '女', '未知']}
        if kind != 'student':
            charge_type = 'class' if kind == 'lesson' else 'month'
            courses = await cls.list_course_names(query_db, charge_type)
            options.update({'*课程名称': courses, '支付方式': cls.PAYMENT_METHODS})
        example = {
            'student': ['15112346789', '麦小小', '男', '2015-03-01', '实验小学', '三年级', '麦妈妈', '', '', ''],
            'lesson': [
                '15112346788',
                '麦小小',
                '男',
                '小学数学',
                '',
                30,
                5,
                2,
                '',
                3000,
                3000,
                '微信',
                '2026-10-01',
                '2027-10-01',
                '',
                '',
            ],
            'month': [
                '15112346788',
                '麦小小',
                '男',
                '托管课',
                '',
                '2026-10-01',
                '2027-01-31',
                '2027-02-28',
                6000,
                6000,
                '现金',
                '2026-10-01',
                '',
                '',
            ],
        }[kind]
        return TeachImportUtil.build_template(
            sheet_name, headers, cls.COMMON_NOTES + cls.KIND_NOTES[kind], options=options, example=example
        )

    @classmethod
    async def list_course_names(cls, query_db: AsyncSession, charge_type: str):
        result = await query_db.execute(
            select(TeachCourse.course_name)
            .join(TeachCoursePrice, TeachCoursePrice.course_id == TeachCourse.id)
            .where(
                TeachCourse.del_flag == 0,
                TeachCourse.status == 1,
                TeachCoursePrice.del_flag == 0,
                TeachCoursePrice.charge_type == charge_type,
            )
            .distinct()
            .order_by(TeachCourse.course_name)
            .limit(500)
        )
        return [row[0] for row in result.all()]

    # ------------------------------------------------------------------ 查找

    @classmethod
    async def find_parent(cls, query_db: AsyncSession, phone: str):
        """
        返回 (base_user, parent)；手机号被非家长账号占用时报错
        """
        base_user = (
            (
                await query_db.execute(
                    select(TeachBaseUser).where(TeachBaseUser.phone == phone, TeachBaseUser.del_flag == '0')
                )
            )
            .scalars()
            .first()
        )
        if not base_user:
            return None, None
        parent = (
            (
                await query_db.execute(
                    select(TeachParent).where(TeachParent.user_id == base_user.id, TeachParent.del_flag == '0')
                )
            )
            .scalars()
            .first()
        )
        if not parent:
            raise ImportRowError('该手机号已被老师或其他账号使用，不能作为家长手机号')
        return base_user, parent

    @classmethod
    async def find_student(cls, query_db: AsyncSession, parent_id: int, student_name: str):
        return (
            (
                await query_db.execute(
                    select(TeachStudent).where(
                        TeachStudent.parent_id == parent_id,
                        TeachStudent.student_name == student_name,
                        TeachStudent.del_flag == '0',
                    )
                )
            )
            .scalars()
            .first()
        )

    @classmethod
    async def find_staff(cls, query_db: AsyncSession, name: str | None, label: str):
        if not name:
            return None
        users = (
            (await query_db.execute(select(SysUser).where(SysUser.nick_name == name, SysUser.del_flag == '0')))
            .scalars()
            .all()
        )
        users = [user for user in users if user.status == '0']
        if not users:
            raise ImportRowError(f'{label}“{name}”不存在或已停用')
        if len(users) > 1:
            raise ImportRowError(f'{label}“{name}”有重名员工，请先在用户管理中区分昵称')
        return users[0].user_id

    @classmethod
    async def find_course(cls, query_db: AsyncSession, course_name: str, charge_type: str):
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
            raise ImportRowError(f'课程“{course_name}”存在重名，请先修改课程名称')
        course = courses[0]
        charge_types = (
            (
                await query_db.execute(
                    select(TeachCoursePrice.charge_type).where(
                        TeachCoursePrice.course_id == course.id, TeachCoursePrice.del_flag == 0
                    )
                )
            )
            .scalars()
            .all()
        )
        if charge_type not in set(charge_types):
            label = '按课时' if charge_type == 'class' else '按月'
            raise ImportRowError(f'课程“{course_name}”未设置{label}收费，请使用对应模板')
        return course

    @classmethod
    async def find_class(cls, query_db: AsyncSession, class_name: str | None, course: TeachCourse):
        if not class_name:
            return None
        classes = (
            (
                await query_db.execute(
                    select(TeachClass).where(TeachClass.class_name == class_name, TeachClass.del_flag == 0)
                )
            )
            .scalars()
            .all()
        )
        classes = [item for item in classes if item.course_id == course.id]
        if not classes:
            raise ImportRowError(f'班级“{class_name}”不存在或不属于课程“{course.course_name}”')
        if len(classes) > 1:
            raise ImportRowError(f'班级“{class_name}”存在重名')
        class_obj = classes[0]
        if class_obj.status != 1 or class_obj.enroll_status == 3:
            raise ImportRowError(f'班级“{class_name}”已停用或已结课')
        return class_obj

    # ------------------------------------------------------------------ 校验

    @classmethod
    async def validate_identity(cls, query_db: AsyncSession, values: dict, seen: dict, line: int):
        phone = TeachImportUtil.phone(values)
        name = TeachImportUtil.required(values, '姓名')
        if len(name) > 50:
            raise ImportRowError('姓名不能超过50字')
        gender_text = values.get('性别')
        if gender_text and gender_text not in cls.GENDER_MAP:
            raise ImportRowError('性别只能填写 男/女/未知')
        _, parent = await cls.find_parent(query_db, phone)
        student = await cls.find_student(query_db, parent.id, name) if parent else None
        key = (phone, name)
        return {
            'phone': phone,
            'name': name,
            'gender': cls.GENDER_MAP.get(gender_text or '未知', '0'),
            'parent': parent,
            'student': student,
            'key': key,
            'first_line': seen.setdefault(key, line),
        }

    @classmethod
    def month_count(cls, start: date, end: date):
        if end < start:
            return 0
        months = (end.year - start.year) * 12 + (end.month - start.month)
        if end.day >= start.day:
            months += 1
        return max(months, 1)

    @classmethod
    async def validate_row(cls, query_db: AsyncSession, kind: str, values: dict, seen: dict, line: int, ctx: dict):
        row = await cls.validate_identity(query_db, values, seen, line)
        if kind == 'student':
            if row['student']:
                raise ImportRowError('学员已存在（重复导入不会覆盖已有资料）')
            if row['first_line'] != line:
                raise ImportRowError(f'与第{row["first_line"]}行重复')
            row['birthday'] = TeachImportUtil.parse_date(values, '出生日期')
            row['follower_user_id'] = await cls.find_staff(query_db, values.get('跟进人'), '跟进人')
            row['advisor_user_id'] = await cls.find_staff(query_db, values.get('学管师'), '学管师')
            return row
        charge_type = 'class' if kind == 'lesson' else 'month'
        course = await cls.find_course(query_db, TeachImportUtil.required(values, '课程名称'), charge_type)
        class_obj = await cls.find_class(query_db, values.get('班级名称'), course)
        receivable = TeachImportUtil.parse_money(values, '应收金额（元）', required=True)
        paid = TeachImportUtil.parse_money(values, '实收金额（元）', required=True)
        payment = values.get('支付方式') or '现金'
        if payment not in cls.PAYMENT_METHODS:
            raise ImportRowError(f'支付方式只能是：{"/".join(cls.PAYMENT_METHODS)}')
        if kind == 'lesson':
            purchased = TeachImportUtil.parse_int(values, '购买课时', required=True)
            gift = TeachImportUtil.parse_int(values, '赠送课时', required=True)
            consumed = TeachImportUtil.parse_int(values, '已上课时', required=True)
            if purchased + gift <= 0:
                raise ImportRowError('购买课时与赠送课时不能同时为0')
            if consumed > purchased + gift:
                raise ImportRowError('已上课时不能超过购买+赠送课时')
            leave_exempt = TeachImportUtil.parse_int(values, '请假免扣剩余次数')
            valid_start, valid_end = None, TeachImportUtil.parse_date(values, '课程到期日期')
            unit = '课时'
        else:
            valid_start = TeachImportUtil.parse_date(values, '课程开始日期', required=True)
            end = TeachImportUtil.parse_date(values, '课程结束日期', required=True)
            if end < valid_start:
                raise ImportRowError('课程结束日期不能早于开始日期')
            gift_end = TeachImportUtil.parse_date(values, '赠送课程日期至')
            if gift_end and gift_end < end:
                raise ImportRowError('赠送课程日期至不能早于课程结束日期')
            purchased = cls.month_count(valid_start, end)
            gift = cls.month_count(end + timedelta(days=1), gift_end) if gift_end and gift_end > end else 0
            consumed, leave_exempt, valid_end, unit = 0, 0, gift_end or end, '月'
        if class_obj:
            used = ctx.setdefault('class_usage', {}).get(class_obj.id, 0) + 1
            ctx['class_usage'][class_obj.id] = used
            if (
                class_obj.max_students
                and class_obj.allow_over_capacity != 1
                and (class_obj.current_students or 0) + used > class_obj.max_students
            ):
                raise ImportRowError(f'班级“{class_obj.class_name}”容量不足')
        row.update(
            {
                'course': course,
                'class_obj': class_obj,
                'charge_type': charge_type,
                'unit': unit,
                'purchased': purchased,
                'gift': gift,
                'consumed': consumed,
                'leave_exempt': leave_exempt,
                'valid_start': valid_start,
                'valid_end': valid_end,
                'receivable': receivable,
                'paid': paid,
                'payment': payment,
                'enroll_date': TeachImportUtil.parse_date(values, '经办日期') or date.today(),
                'performance_owner': values.get('业绩归属人'),
                'remark': (values.get('备注') or '')[:200],
            }
        )
        return row

    # ------------------------------------------------------------------ 写入

    @classmethod
    async def ensure_student(cls, query_db: AsyncSession, row: dict, cache: dict, current_user_name: str):
        if row['student']:
            return row['student']
        if row['key'] in cache['students']:
            return cache['students'][row['key']]
        parent = row['parent'] or cache['parents'].get(row['phone'])
        if not parent:
            base_user = TeachBaseUser(
                phone=row['phone'],
                password_hash=PwdUtil.get_password_hash(secrets.token_urlsafe(16)),
                user_type=2,
                status=1,
                create_by=current_user_name,
                update_by=current_user_name,
                remark='学员导入自动创建',
            )
            query_db.add(base_user)
            await query_db.flush()
            parent = TeachParent(
                user_id=base_user.id,
                parent_name=(row.get('parent_name') or f'{row["name"]}家长')[:50],
                status='0',
                create_by=current_user_name,
                update_by=current_user_name,
                remark='学员导入自动创建',
            )
            query_db.add(parent)
            await query_db.flush()
            cache['parents'][row['phone']] = parent
        student = TeachStudent(
            parent_id=parent.id,
            student_name=row['name'],
            gender=row['gender'],
            birthday=row.get('birthday'),
            school_name=row.get('school_name'),
            grade=row.get('grade'),
            status='0',
            follower_user_id=row.get('follower_user_id'),
            advisor_user_id=row.get('advisor_user_id'),
            create_by=current_user_name,
            update_by=current_user_name,
            remark=row.get('remark') if not row.get('course') else None,
        )
        query_db.add(student)
        await query_db.flush()
        cache['students'][row['key']] = student
        return student

    @classmethod
    async def write_enrollment(cls, query_db: AsyncSession, row: dict, student: TeachStudent, batch_no: str, user: str):
        course = row['course']
        class_obj = row['class_obj']
        remark = f'支付方式：{row["payment"]}' + (f'；{row["remark"]}' if row['remark'] else '')
        order = await TeachEnrollmentDao.add_enrollment_order(
            query_db,
            TeachEnrollmentOrder(
                order_no=f'IM{datetime.now().strftime("%Y%m%d%H%M%S%f")}{secrets.token_hex(2).upper()}',
                student_id=student.id,
                student_name=student.student_name,
                parent_phone=row['phone'],
                order_type='import',
                order_source='导入',
                enroll_date=row['enroll_date'],
                item_count=1,
                total_amount=row['receivable'],
                discount_amount=Decimal('0'),
                receivable_amount=row['receivable'],
                paid_amount=row['paid'],
                status='paid',
                performance_owner=row['performance_owner'],
                remark=remark,
                create_by=user,
                update_by=user,
            ),
        )
        quantity = row['purchased']
        unit_price = (row['receivable'] / quantity).quantize(Decimal('0.01')) if quantity else Decimal('0')
        order_item = await TeachEnrollmentDao.add_enrollment_order_item(
            query_db,
            TeachEnrollmentOrderItem(
                order_id=order.id,
                student_id=student.id,
                item_type='course',
                item_id=course.id,
                item_name=course.course_name,
                charge_type=row['charge_type'],
                unit=row['unit'],
                quantity=quantity,
                gift_quantity=row['gift'],
                leave_exempt_count=row['leave_exempt'],
                unit_price=unit_price,
                total_price=row['receivable'],
                subtotal_price=row['receivable'],
                start_date=row['valid_start'],
                end_date=row['valid_end'],
                class_id=class_obj.id if class_obj else None,
                class_name=class_obj.class_name if class_obj else None,
                remark='Excel 导入',
                create_by=user,
                update_by=user,
            ),
        )
        total = row['purchased'] + row['gift']
        account = await TeachEnrollmentDao.add_student_course_account(
            query_db,
            TeachStudentCourseAccount(
                student_id=student.id,
                course_id=course.id,
                course_name=course.course_name,
                order_id=order.id,
                order_item_id=order_item.id,
                charge_type=row['charge_type'],
                unit=row['unit'],
                purchased_quantity=row['purchased'],
                gift_quantity=row['gift'],
                consumed_quantity=row['consumed'],
                remaining_quantity=total - row['consumed'],
                leave_exempt_count=row['leave_exempt'],
                valid_start_date=row['valid_start'],
                valid_end_date=row['valid_end'],
                class_id=class_obj.id if class_obj else None,
                class_name=class_obj.class_name if class_obj else None,
                remark='Excel 导入',
                create_by=user,
                update_by=user,
            ),
        )
        await TeachStudentAccountDao.add_log(
            query_db,
            TeachCourseAccountLog(
                batch_no=batch_no,
                op_type='import',
                account_id=account.id,
                student_id=student.id,
                student_name=student.student_name,
                course_id=course.id,
                course_name=course.course_name,
                change_quantity=account.remaining_quantity,
                before_remaining=0,
                after_remaining=account.remaining_quantity,
                after_status='active',
                after_valid_start=account.valid_start_date,
                after_valid_end=account.valid_end_date,
                related_order_id=order.id,
                reason=f'导入：已上{row["consumed"]}{row["unit"]}',
                create_by=user,
                create_time=datetime.now(),
            ),
        )
        if class_obj:
            await TeachClassService.add_student_from_enrollment_services(
                query_db, class_obj.id, student.id, account, order_item, user
            )

    @classmethod
    async def import_services(cls, query_db: AsyncSession, kind: str, file, current_user_name: str):
        _, headers = cls.get_kind(kind)
        required = [header.lstrip('*') for header in headers if header.startswith('*')]
        rows = await TeachImportUtil.read_rows(file, required)
        errors, parsed, seen, ctx = [], [], {}, {}
        for line, values in rows:
            try:
                row = await cls.validate_row(query_db, kind, values, seen, line, ctx)
                if kind == 'student':
                    row.update(
                        {
                            'school_name': (values.get('就读学校') or '')[:100] or None,
                            'grade': (values.get('当前年级') or '')[:20] or None,
                            'parent_name': values.get('家长姓名'),
                            'remark': (values.get('备注') or '')[:500] or None,
                        }
                    )
                parsed.append(row)
            except ImportRowError as e:
                errors.append({'row': line, 'message': str(e)})
        if errors:
            return TeachImportUtil.result(len(rows), errors)
        batch_no = f'IM{datetime.now().strftime("%Y%m%d%H%M%S%f")}'
        cache = {'parents': {}, 'students': {}}
        try:
            created_students = 0
            for row in parsed:
                existed = bool(row['student']) or row['key'] in cache['students']
                student = await cls.ensure_student(query_db, row, cache, current_user_name)
                created_students += 0 if existed else 1
                if kind != 'student':
                    await cls.write_enrollment(query_db, row, student, batch_no, current_user_name)
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise e
        return TeachImportUtil.result(
            len(rows), [], len(parsed), {'createdStudents': created_students, 'batchNo': batch_no}
        )
