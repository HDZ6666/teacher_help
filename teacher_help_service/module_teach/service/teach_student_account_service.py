from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_enrollment_dao import TeachEnrollmentDao
from module_teach.dao.teach_student_account_dao import TeachStudentAccountDao
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.entity.do.teach_enrollment_order_do import (
    TeachCourseAccountLog,
    TeachEnrollmentOrder,
    TeachEnrollmentOrderItem,
    TeachStudentCourseAccount,
)
from module_teach.entity.vo.teach_student_account_vo import (
    ChangeCourseValidityModel,
    ClearCourseAccountModel,
    CompleteCourseAccountModel,
    ResumeCourseAccountModel,
    StopCourseAccountModel,
    TeachCourseAccountPageQueryModel,
    TransferCourseAccountModel,
)
from module_teach.service.teach_class_service import TeachClassService
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachStudentAccountService:
    """
    学员课程账户（报读情况）服务层：报读列表、批量转课、课时清零、改有效期、停课/复课/结课、收据、学员详情聚合

    所有会改变课程账户的操作都会按ID升序对账户加行锁（与点名扣课同一把锁），并逐条写入 teach_course_account_log。
    """

    STATUS_LABELS = {
        'active': '有效',
        'stopped': '停课',
        'completed': '结课',
        'transferred': '已转出',
    }
    OP_LABELS = {
        'transfer_out': '转出',
        'transfer_in': '转入',
        'clear': '课时清零',
        'validity': '修改有效期',
        'stop': '停课',
        'resume': '复课',
        'complete': '结课',
        'import': '导入',
    }
    CHARGE_UNITS = {'class': '课时', 'lesson': '课时', 'month': '月', 'day': '天'}
    ATTENDANCE_LABELS = {1: '到课', 2: '迟到', 3: '请假', 4: '未到'}
    CHECKIN_LABELS = {0: '未到', 1: '出勤', 2: '迟到', 3: '请假', 4: '缺勤'}

    @classmethod
    def make_batch_no(cls, prefix: str = 'CA'):
        return f'{prefix}{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def make_page(cls, rows: list, total: int, page_num: int, page_size: int):
        return PageResponseModel(
            rows=rows, pageNum=page_num, pageSize=page_size, total=total, hasNext=total > page_num * page_size
        )

    @classmethod
    def mask_phone(cls, phone: str | None):
        if not phone or len(phone) < 7:
            return phone or ''
        return f'{phone[:3]}****{phone[-4:]}'

    @classmethod
    def format_account(cls, account: TeachStudentCourseAccount, student=None, phone=None, order_no=None):
        row = CamelCaseUtil.transform_result(account)
        row['statusName'] = cls.STATUS_LABELS.get(account.status, account.status)
        row['orderNo'] = order_no
        if student is not None:
            row['studentName'] = student.student_name
            row['followerUserId'] = student.follower_user_id
            row['advisorUserId'] = student.advisor_user_id
        row['phone'] = cls.mask_phone(phone)
        row['totalQuantity'] = (account.purchased_quantity or 0) + (account.gift_quantity or 0)
        return row

    # ------------------------------------------------------------------ 查询

    @classmethod
    async def get_account_list_services(cls, query_db: AsyncSession, query_object: TeachCourseAccountPageQueryModel):
        rows, total = await TeachStudentAccountDao.get_account_list(query_db, query_object)
        result = [cls.format_account(account, student, phone, order_no) for account, student, phone, order_no in rows]
        return cls.make_page(result, total, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_account_logs_services(cls, query_db: AsyncSession, student_id: int | None, account_id: int | None):
        if not student_id and not account_id:
            raise ServiceException(message='请指定学员或课程账户')
        logs = await TeachStudentAccountDao.get_logs(query_db, student_id, account_id)
        rows = []
        for log in logs:
            row = CamelCaseUtil.transform_result(log)
            row['opTypeName'] = cls.OP_LABELS.get(log.op_type, log.op_type)
            row['beforeStatusName'] = cls.STATUS_LABELS.get(log.before_status, log.before_status)
            row['afterStatusName'] = cls.STATUS_LABELS.get(log.after_status, log.after_status)
            rows.append(row)
        return rows

    # ------------------------------------------------------------------ 公共

    @classmethod
    async def lock_accounts(cls, query_db: AsyncSession, account_ids: list[int], allowed_status: tuple, action: str):
        ids = sorted(set(account_ids))
        accounts = await TeachStudentAccountDao.get_accounts_for_update(query_db, ids)
        if len(accounts) != len(ids):
            raise ServiceException(message='部分课程账户不存在或已删除，请刷新后重试')
        for account in accounts:
            if account.status not in allowed_status:
                status_name = cls.STATUS_LABELS.get(account.status, account.status)
                raise ServiceException(message=f'课程账户（{account.course_name}）当前为“{status_name}”，不能{action}')
        return accounts

    @classmethod
    async def get_student_name_map(cls, query_db: AsyncSession, accounts: list[TeachStudentCourseAccount]):
        name_map = {}
        for student_id in sorted({account.student_id for account in accounts}):
            student_result = await TeachStudentDao.get_teach_student_by_id(query_db, student_id)
            name_map[student_id] = student_result[0].student_name if student_result else ''
        return name_map

    @classmethod
    async def write_log(
        cls,
        query_db: AsyncSession,
        batch_no: str,
        op_type: str,
        account: TeachStudentCourseAccount,
        student_name: str,
        current_user_name: str,
        *,
        before_remaining: int | None,
        before_status: str | None,
        before_valid: tuple = (None, None),
        reason: str | None = None,
        related_account_id: int | None = None,
        related_order_id: int | None = None,
    ):
        after_remaining = account.remaining_quantity or 0
        await TeachStudentAccountDao.add_log(
            query_db,
            TeachCourseAccountLog(
                batch_no=batch_no,
                op_type=op_type,
                account_id=account.id,
                student_id=account.student_id,
                student_name=student_name,
                course_id=account.course_id,
                course_name=account.course_name,
                change_quantity=after_remaining - (before_remaining or 0) if before_remaining is not None else 0,
                before_remaining=before_remaining,
                after_remaining=after_remaining,
                before_status=before_status,
                after_status=account.status,
                before_valid_start=before_valid[0],
                before_valid_end=before_valid[1],
                after_valid_start=account.valid_start_date,
                after_valid_end=account.valid_end_date,
                related_account_id=related_account_id,
                related_order_id=related_order_id,
                reason=reason,
                create_by=current_user_name,
                create_time=datetime.now(),
            ),
        )

    @classmethod
    def touch(cls, account: TeachStudentCourseAccount, current_user_name: str):
        account.update_by = current_user_name
        account.update_time = datetime.now()

    @classmethod
    async def refresh_classes(cls, query_db: AsyncSession, class_ids):
        for class_id in sorted(set(class_ids)):
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
            graduated = bool(class_obj and class_obj.enroll_status == 3)
            await TeachClassDao.refresh_class_student_count(query_db, class_id)
            # 已结课的班级不因人数刷新被改回招生中
            if graduated:
                await TeachStudentAccountDao.set_class_enroll_status(query_db, class_id, 3)

    # ------------------------------------------------------------------ 批量转课

    @classmethod
    async def transfer_services(
        cls, query_db: AsyncSession, page_object: TransferCourseAccountModel, current_user_name: str
    ):
        """
        批量转课：所选账户的全部剩余数量转入目标课程（每个账户生成一张 0 元“转课”订单与新的课程账户）。
        金额不做折算，转入账户请假免扣次数为 0（与原型提示一致：转入后需手动编辑）。
        """
        course = await TeachCourseDao.get_teach_course_by_id(query_db, page_object.target_course_id)
        if not course or course.status != 1:
            raise ServiceException(message='转入课程不存在或已停用')
        target_prices = await TeachCourseDao.get_prices_by_course_id(query_db, course.id)
        target_charge_types = {price.charge_type for price in target_prices}
        class_obj = None
        if page_object.target_class_id:
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, page_object.target_class_id)
            if not class_obj or class_obj.status != 1 or class_obj.enroll_status == 3:
                raise ServiceException(message='转入班级不存在或不可招生')
            if class_obj.course_id != course.id:
                raise ServiceException(message='转入班级与转入课程不对应')
        enroll_date = page_object.enroll_date or date.today()
        batch_no = cls.make_batch_no('TR')
        try:
            accounts = await cls.lock_accounts(query_db, page_object.account_ids, ('active',), '转课')
            if len({account.student_id for account in accounts}) != len(accounts):
                raise ServiceException(message='同一学员一次只能转出一个课程账户')
            if class_obj and class_obj.max_students and class_obj.allow_over_capacity != 1:
                if (class_obj.current_students or 0) + len(accounts) > class_obj.max_students:
                    raise ServiceException(message=f'班级（{class_obj.class_name}）容量不足')
            name_map = await cls.get_student_name_map(query_db, accounts)
            affected_classes = set()
            created = []
            for account in accounts:
                student_name = name_map.get(account.student_id, '')
                remaining = account.remaining_quantity or 0
                if remaining <= 0:
                    raise ServiceException(message=f'{student_name}的{account.course_name}没有可转出的剩余数量')
                if account.course_id == course.id:
                    raise ServiceException(message=f'{student_name}的转出课程与转入课程相同，无需转课')
                charge_type = account.charge_type
                if target_charge_types and charge_type not in target_charge_types:
                    raise ServiceException(
                        message=f'{student_name}的{account.course_name}收费方式与转入课程不一致，不能直接转课'
                    )
                before_status, before_valid = account.status, (account.valid_start_date, account.valid_end_date)
                transfer_remark = f'由{account.course_name}转入{remaining}{account.unit or ""}'
                transfer_remark += f'；{page_object.reason}' if page_object.reason else ''
                order = await TeachEnrollmentDao.add_enrollment_order(
                    query_db,
                    TeachEnrollmentOrder(
                        order_no=f'TR{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}',
                        student_id=account.student_id,
                        student_name=student_name,
                        order_type='transfer',
                        order_source='转课',
                        enroll_date=enroll_date,
                        item_count=1,
                        status='paid',
                        remark=transfer_remark[:500],
                        create_by=current_user_name,
                        update_by=current_user_name,
                    ),
                )
                if page_object.validity_mode == 'unified':
                    valid_start, valid_end = page_object.valid_start_date or enroll_date, page_object.valid_end_date
                else:
                    valid_start, valid_end = account.valid_start_date, account.valid_end_date
                order_item = await TeachEnrollmentDao.add_enrollment_order_item(
                    query_db,
                    TeachEnrollmentOrderItem(
                        order_id=order.id,
                        student_id=account.student_id,
                        item_type='course',
                        item_id=course.id,
                        item_name=course.course_name,
                        charge_type=charge_type,
                        unit=account.unit,
                        quantity=remaining,
                        gift_quantity=0,
                        unit_price=Decimal('0'),
                        total_price=Decimal('0'),
                        subtotal_price=Decimal('0'),
                        start_date=valid_start,
                        end_date=valid_end,
                        validity_type=account.validity_type,
                        class_id=class_obj.id if class_obj else None,
                        class_name=class_obj.class_name if class_obj else None,
                        remark=f'转课：原课程账户{account.id}',
                        create_by=current_user_name,
                        update_by=current_user_name,
                    ),
                )
                new_account = await TeachEnrollmentDao.add_student_course_account(
                    query_db,
                    TeachStudentCourseAccount(
                        student_id=account.student_id,
                        course_id=course.id,
                        course_name=course.course_name,
                        order_id=order.id,
                        order_item_id=order_item.id,
                        charge_type=charge_type,
                        unit=account.unit,
                        purchased_quantity=remaining,
                        gift_quantity=0,
                        remaining_quantity=remaining,
                        leave_exempt_count=0,
                        valid_start_date=valid_start,
                        valid_end_date=valid_end,
                        validity_type=account.validity_type,
                        class_id=class_obj.id if class_obj else None,
                        class_name=class_obj.class_name if class_obj else None,
                        remark=f'由课程账户{account.id}（{account.course_name}）转入',
                        create_by=current_user_name,
                        update_by=current_user_name,
                    ),
                )
                account.transferred_quantity = (account.transferred_quantity or 0) + remaining
                account.remaining_quantity = 0
                account.status = 'transferred'
                account.complete_date = enroll_date
                cls.touch(account, current_user_name)
                affected_classes.update(
                    await TeachStudentAccountDao.remove_account_from_classes(query_db, account.id, current_user_name)
                )
                await cls.write_log(
                    query_db,
                    batch_no,
                    'transfer_out',
                    account,
                    student_name,
                    current_user_name,
                    before_remaining=remaining,
                    before_status=before_status,
                    before_valid=before_valid,
                    reason=page_object.reason,
                    related_account_id=new_account.id,
                    related_order_id=order.id,
                )
                await cls.write_log(
                    query_db,
                    batch_no,
                    'transfer_in',
                    new_account,
                    student_name,
                    current_user_name,
                    before_remaining=0,
                    before_status=None,
                    reason=page_object.reason,
                    related_account_id=account.id,
                    related_order_id=order.id,
                )
                if class_obj:
                    await TeachClassService.ensure_student_in_class(
                        query_db, class_obj, account.student_id, current_user_name, new_account, order_item
                    )
                    affected_classes.add(class_obj.id)
                created.append({'fromAccountId': account.id, 'toAccountId': new_account.id, 'orderNo': order.order_no})
            await cls.refresh_classes(query_db, affected_classes)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f'转课成功，共转出{len(created)}个课程账户',
                result={'batchNo': batch_no, 'items': created},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 课时清零

    @classmethod
    async def clear_services(cls, query_db: AsyncSession, page_object: ClearCourseAccountModel, current_user_name: str):
        batch_no = cls.make_batch_no('CL')
        try:
            accounts = await cls.lock_accounts(query_db, page_object.account_ids, ('active', 'stopped'), '课时清零')
            name_map = await cls.get_student_name_map(query_db, accounts)
            cleared_total = 0
            for account in accounts:
                remaining = account.remaining_quantity or 0
                if remaining <= 0:
                    continue
                account.cleared_quantity = (account.cleared_quantity or 0) + remaining
                account.remaining_quantity = 0
                cls.touch(account, current_user_name)
                cleared_total += remaining
                await cls.write_log(
                    query_db,
                    batch_no,
                    'clear',
                    account,
                    name_map.get(account.student_id, ''),
                    current_user_name,
                    before_remaining=remaining,
                    before_status=account.status,
                    before_valid=(account.valid_start_date, account.valid_end_date),
                    reason=page_object.reason,
                )
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f'课时清零成功，共清零{cleared_total}',
                result={'batchNo': batch_no, 'clearedQuantity': cleared_total},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 改有效期

    @classmethod
    async def change_validity_services(
        cls, query_db: AsyncSession, page_object: ChangeCourseValidityModel, current_user_name: str
    ):
        batch_no = cls.make_batch_no('VD')
        try:
            accounts = await cls.lock_accounts(query_db, page_object.account_ids, ('active', 'stopped'), '修改有效期')
            name_map = await cls.get_student_name_map(query_db, accounts)
            for account in accounts:
                before_valid = (account.valid_start_date, account.valid_end_date)
                if page_object.valid_start_date:
                    account.valid_start_date = page_object.valid_start_date
                if account.valid_start_date and account.valid_start_date > page_object.valid_end_date:
                    raise ServiceException(
                        message=f'{name_map.get(account.student_id, "")}的{account.course_name}结束日期早于开始日期'
                    )
                account.valid_end_date = page_object.valid_end_date
                cls.touch(account, current_user_name)
                await cls.write_log(
                    query_db,
                    batch_no,
                    'validity',
                    account,
                    name_map.get(account.student_id, ''),
                    current_user_name,
                    before_remaining=account.remaining_quantity,
                    before_status=account.status,
                    before_valid=before_valid,
                    reason=page_object.reason,
                )
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'已修改{len(accounts)}个课程账户的有效期', result={'batchNo': batch_no}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 停课 / 复课 / 结课

    @classmethod
    async def stop_services(cls, query_db: AsyncSession, page_object: StopCourseAccountModel, current_user_name: str):
        batch_no = cls.make_batch_no('ST')
        try:
            accounts = await cls.lock_accounts(query_db, page_object.account_ids, ('active',), '停课')
            name_map = await cls.get_student_name_map(query_db, accounts)
            for account in accounts:
                account.status = 'stopped'
                account.stop_date = page_object.stop_date
                account.planned_resume_date = page_object.planned_resume_date
                account.stop_reason = page_object.reason
                cls.touch(account, current_user_name)
                await cls.write_log(
                    query_db,
                    batch_no,
                    'stop',
                    account,
                    name_map.get(account.student_id, ''),
                    current_user_name,
                    before_remaining=account.remaining_quantity,
                    before_status='active',
                    before_valid=(account.valid_start_date, account.valid_end_date),
                    reason=page_object.reason,
                )
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'已停课{len(accounts)}个课程账户', result={'batchNo': batch_no}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def resume_services(
        cls, query_db: AsyncSession, page_object: ResumeCourseAccountModel, current_user_name: str
    ):
        """
        复课：课程结束日期按停课天数（复课日期 - 停课日期）顺延（原型“复课后自动顺延截至日期”）
        """
        resume_date = page_object.resume_date or date.today()
        batch_no = cls.make_batch_no('RS')
        try:
            accounts = await cls.lock_accounts(query_db, page_object.account_ids, ('stopped',), '复课')
            name_map = await cls.get_student_name_map(query_db, accounts)
            for account in accounts:
                before_valid = (account.valid_start_date, account.valid_end_date)
                stop_date = account.stop_date or resume_date
                if resume_date < stop_date:
                    raise ServiceException(
                        message=f'{name_map.get(account.student_id, "")}的复课日期不能早于停课日期{stop_date}'
                    )
                stopped_days = (resume_date - stop_date).days
                if account.valid_end_date and stopped_days > 0:
                    account.valid_end_date = account.valid_end_date + timedelta(days=stopped_days)
                account.status = 'active'
                account.stop_date = None
                account.planned_resume_date = None
                account.stop_reason = None
                cls.touch(account, current_user_name)
                reason = f'停课{stopped_days}天' + (f'；{page_object.reason}' if page_object.reason else '')
                await cls.write_log(
                    query_db,
                    batch_no,
                    'resume',
                    account,
                    name_map.get(account.student_id, ''),
                    current_user_name,
                    before_remaining=account.remaining_quantity,
                    before_status='stopped',
                    before_valid=before_valid,
                    reason=reason,
                )
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'已复课{len(accounts)}个课程账户', result={'batchNo': batch_no}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def complete_services(
        cls, query_db: AsyncSession, page_object: CompleteCourseAccountModel, current_user_name: str
    ):
        """
        结课：剩余数量全部清零（计入已清零数量）、移出对应班级、账户状态置为结课，不可再点名扣课
        """
        batch_no = cls.make_batch_no('CP')
        try:
            accounts = await cls.lock_accounts(query_db, page_object.account_ids, ('active', 'stopped'), '结课')
            name_map = await cls.get_student_name_map(query_db, accounts)
            affected_classes = set()
            for account in accounts:
                before_status, remaining = account.status, account.remaining_quantity or 0
                account.cleared_quantity = (account.cleared_quantity or 0) + remaining
                account.remaining_quantity = 0
                account.status = 'completed'
                account.complete_date = date.today()
                account.stop_date = None
                account.planned_resume_date = None
                cls.touch(account, current_user_name)
                affected_classes.update(
                    await TeachStudentAccountDao.remove_account_from_classes(query_db, account.id, current_user_name)
                )
                await cls.write_log(
                    query_db,
                    batch_no,
                    'complete',
                    account,
                    name_map.get(account.student_id, ''),
                    current_user_name,
                    before_remaining=remaining,
                    before_status=before_status,
                    before_valid=(account.valid_start_date, account.valid_end_date),
                    reason=page_object.reason,
                )
            await cls.refresh_classes(query_db, affected_classes)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'已结课{len(accounts)}个课程账户', result={'batchNo': batch_no}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 收据

    @classmethod
    async def get_receipt_services(cls, query_db: AsyncSession, order_id: int):
        order, items = await TeachStudentAccountDao.get_order_with_items(query_db, order_id)
        if not order:
            raise ServiceException(message='订单不存在')
        receipt = CamelCaseUtil.transform_result(order)
        receipt['items'] = CamelCaseUtil.transform_result(list(items))
        receipt['debtAmount'] = max((order.receivable_amount or Decimal('0')) - (order.paid_amount or Decimal('0')), 0)
        receipt['parentPhone'] = cls.mask_phone(order.parent_phone)
        receipt['printTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return receipt

    # ------------------------------------------------------------------ 学员详情页签

    @classmethod
    async def get_student_lessons_services(cls, query_db: AsyncSession, student_id: int, page_num: int, page_size: int):
        rows, total = await TeachStudentAccountDao.get_student_lessons(query_db, student_id, page_num, page_size)
        result = []
        for detail, attendance in rows:
            result.append(
                {
                    'detailId': detail.id,
                    'attendanceId': attendance.id,
                    'classDate': attendance.class_date,
                    'startTime': attendance.start_time,
                    'endTime': attendance.end_time,
                    'className': attendance.class_name,
                    'courseName': attendance.course_name,
                    'teacherName': attendance.teacher_name,
                    'classroom': attendance.classroom,
                    'status': detail.status,
                    'statusName': cls.ATTENDANCE_LABELS.get(detail.status, str(detail.status)),
                    'deductQuantity': detail.deduct_quantity,
                    'afterRemaining': detail.after_remaining,
                    'makeupFlag': detail.makeup_flag,
                    'remark': detail.remark,
                }
            )
        return cls.make_page(result, total, page_num, page_size)

    @classmethod
    async def get_student_checkins_services(
        cls, query_db: AsyncSession, student_id: int, page_num: int, page_size: int
    ):
        rows, total = await TeachStudentAccountDao.get_student_checkins(query_db, student_id, page_num, page_size)
        result = []
        for attendance, event in rows:
            result.append(
                {
                    'id': attendance.id,
                    'eventId': event.id,
                    'eventDate': event.event_date,
                    'startTime': event.start_time,
                    'endTime': event.end_time,
                    'className': event.class_name,
                    'courseName': event.course_name,
                    'classroom': event.classroom,
                    'status': attendance.status,
                    'statusName': cls.CHECKIN_LABELS.get(attendance.status, str(attendance.status)),
                    'checkInTime': attendance.check_in_time,
                    'checkInMethod': {'Q': '扫码', 'M': '手动'}.get(attendance.check_in_method or '', '-'),
                    'notes': attendance.notes,
                }
            )
        return cls.make_page(result, total, page_num, page_size)

    @classmethod
    async def get_student_comments_services(
        cls, query_db: AsyncSession, student_id: int, page_num: int, page_size: int
    ):
        rows, total = await TeachStudentAccountDao.get_student_comments(query_db, student_id, page_num, page_size)
        return cls.make_page(CamelCaseUtil.transform_result(list(rows)), total, page_num, page_size)
