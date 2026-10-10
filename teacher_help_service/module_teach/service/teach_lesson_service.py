from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_lesson_dao import TeachLessonDao
from module_teach.dao.teach_schedule_attendance_dao import TeachScheduleAttendanceDao
from module_teach.dao.teach_schedule_event_dao import TeachScheduleEventDao
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.entity.do.teach_class_do import TeachClassAttendanceDetail
from module_teach.entity.do.teach_enrollment_order_do import TeachCourseAccountLog
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.entity.vo.teach_lesson_vo import (
    AddTempStudentModel,
    EditAttendanceDetailModel,
    EditAttendanceRecordModel,
    MakeupClassModel,
    RescheduleLessonModel,
    WeeklyScheduleModel,
)
from module_teach.service.teach_class_service import TeachClassService
from module_teach.service.teach_schedule_event_service import TeachScheduleEventService


class TeachLessonService:
    """
    课次操作服务：课表调课、临时学员、按周重复排课；上课记录修改单个学员点名、编辑课次、开补课班

    加锁顺序与点名提交/撤销点名一致：班级行 -> 点名记录 -> 点名明细 -> 课程账户（按ID），避免死锁。
    """

    MAX_WEEKLY_EVENTS = 100
    STATUS_LABELS = TeachClassService.ATTENDANCE_STATUS_LABELS

    @classmethod
    def append_text(cls, origin: str | None, note: str, limit: int = 500):
        text = f'{origin}；{note}' if origin else note
        return text[-limit:]

    @classmethod
    def fmt_time(cls, value: datetime | None):
        return value.strftime('%Y-%m-%d %H:%M') if value else '-'

    @classmethod
    async def get_event(cls, query_db: AsyncSession, event_id: int):
        event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, event_id)
        if not event or str(event.del_flag) != '0':
            raise ServiceException(message='课次不存在或已删除')
        return event

    @classmethod
    async def resolve_course_account(cls, query_db: AsyncSession, student_id: int, course_id: int, account_id=None):
        """
        临时学员/补课学员的扣课账户：指定账户须属于该学员、同一课程且为有效状态；未指定取该课程最新有效账户
        """
        if account_id:
            account = await TeachClassDao.get_course_account_by_id(query_db, account_id)
            if not account or account.student_id != student_id or account.course_id != course_id:
                raise ServiceException(message='课程账户不属于该学员或与课次课程不一致')
            if account.status != 'active':
                raise ServiceException(message='课程账户不是有效状态（停课/结课/已转出），不能上课扣课')
            return account
        return await TeachClassDao.get_student_course_account(query_db, student_id, course_id)

    @classmethod
    async def recount_attendance(cls, query_db: AsyncSession, attendance, operator: str):
        """
        按有效点名明细重算点名记录人数/扣课合计与课次出勤缓存
        """
        await query_db.flush()
        details = await TeachLessonDao.get_active_details(query_db, attendance.id)
        count = {1: 0, 2: 0, 3: 0, 4: 0}
        for detail in details:
            count[detail.status] = count.get(detail.status, 0) + 1
        attendance.student_count = len(details)
        attendance.present_count = count[1]
        attendance.late_count = count[2]
        attendance.leave_count = count[3]
        attendance.absent_count = count[4]
        attendance.deducted_quantity = sum(detail.deduct_quantity or 0 for detail in details)
        attendance.update_by = operator
        attendance.update_time = datetime.now()
        if attendance.event_id:
            event = await TeachScheduleEventDao.get_raw_schedule_event_by_id(query_db, attendance.event_id)
            if event:
                planned = len(details)
                event.cached_planned = planned
                event.cached_present = count[1]
                event.cached_late = count[2]
                event.cached_excused = count[3]
                event.cached_absent = count[4]
                event.cached_rate = round((count[1] + count[2]) / planned * 100, 2) if planned else 0
                event.update_by = operator
                event.update_time = datetime.now()

    @classmethod
    def change_account(cls, account, delta: int, operator: str):
        """
        delta > 0 扣课，delta < 0 退回课时；返回 (变动前剩余, 变动后剩余)
        """
        before = account.remaining_quantity or 0
        account.remaining_quantity = before - delta
        account.consumed_quantity = max((account.consumed_quantity or 0) + delta, 0)
        account.update_by = operator
        account.update_time = datetime.now()
        return before, account.remaining_quantity

    # ------------------------------------------------------------------ 课表：调课

    @classmethod
    async def reschedule_services(cls, query_db: AsyncSession, page_object: RescheduleLessonModel, operator: str):
        event = await cls.get_event(query_db, page_object.event_id)
        if event.status not in ('0', '1'):
            raise ServiceException(message='只有未点名、未取消的课次可以调课')
        if not event.class_id:
            raise ServiceException(message='课次未关联班级，不能调课')
        try:
            await TeachClassDao.get_teach_class_by_id(query_db, event.class_id, for_update=True)
            if await TeachClassDao.get_class_attendance_by_event_id(query_db, event.id, for_update=True):
                raise ServiceException(message='该课次已点名，不能调课；如需更正请在上课记录中编辑课次')
            teacher_id = page_object.teacher_id or event.teacher_id
            classroom = page_object.classroom if page_object.classroom is not None else event.classroom
            class_obj, _, teacher = await TeachScheduleEventService.validate_schedule_base(
                query_db,
                event.class_id,
                event.course_id,
                teacher_id,
                page_object.start_time,
                page_object.end_time,
                classroom,
                exclude_event_id=event.id,
            )
            old_teacher = await TeachClassDao.get_teacher_by_id(query_db, event.teacher_id)
            note = (
                f'调课：{cls.fmt_time(event.start_time)}-{event.end_time.strftime("%H:%M")}'
                f'/{old_teacher.teacher_name if old_teacher else "-"}/{event.classroom or "-"}'
                f' → {cls.fmt_time(page_object.start_time)}-{page_object.end_time.strftime("%H:%M")}'
                f'/{teacher.teacher_name}/{classroom or class_obj.classroom or "-"}'
                f'（{operator}，原因：{page_object.reason or "无"}）'
            )
            event.start_time = page_object.start_time
            event.end_time = page_object.end_time
            event.event_date = page_object.start_time.date()
            event.teacher_id = teacher.id
            event.classroom = classroom or class_obj.classroom
            event.remark = cls.append_text(event.remark, note)
            event.update_by = operator
            event.update_time = datetime.now()
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='调课成功', result={'id': event.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 课表：临时学员

    @classmethod
    async def add_temp_student_services(cls, query_db: AsyncSession, page_object: AddTempStudentModel, operator: str):
        event = await cls.get_event(query_db, page_object.event_id)
        if event.status == '3':
            raise ServiceException(message='已取消的课次不能添加学员')
        if not event.class_id:
            raise ServiceException(message='课次未关联班级，不能添加临时学员')
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, page_object.student_id)
        if not student_result:
            raise ServiceException(message='学员不存在')
        student = student_result[0]
        try:
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, event.class_id, for_update=True)
            if not class_obj:
                raise ServiceException(message='班级不存在')
            if await TeachLessonDao.get_roster_row(query_db, event.id, student.id):
                raise ServiceException(message='该学员已在本课次名单中')
            member = await TeachClassDao.get_active_class_student(query_db, class_obj.id, student.id)
            if member:
                account = (
                    await TeachClassDao.get_course_account_by_id(query_db, member.course_account_id)
                    if member.course_account_id
                    else None
                )
            else:
                account = await cls.resolve_course_account(
                    query_db, student.id, event.course_id, page_object.course_account_id
                )
                if not account:
                    raise ServiceException(message='该学员没有本课程的有效课程账户，不能作为临时学员上课')
            attendance = await TeachClassDao.get_class_attendance_by_event_id(query_db, event.id, for_update=True)
            roster = TeachScheduleAttendance(
                event_id=event.id,
                student_id=student.id,
                status=0,
                is_countable=1,
                is_temp=0 if member else 1,
                course_account_id=None if member else account.id,
                notes=page_object.remark,
                create_by=operator,
                update_by=operator,
            )
            if attendance is None:
                await TeachScheduleAttendanceDao.add_attendance(query_db, roster)
                event.cached_planned = (event.cached_planned or 0) + 1
                event.update_by = operator
                event.update_time = datetime.now()
                await query_db.commit()
                return CrudResponseModel(
                    is_success=True, message='已加入本课次名单，点名时一并点名扣课', result={'eventId': event.id}
                )
            # 课次已点名：直接补一条点名明细并按规则扣课
            if page_object.status is None:
                raise ServiceException(message='该课次已点名，请选择到课状态')
            leave_map = await TeachClassService.get_approved_leave_map(
                query_db, class_obj.id, [student.id], event.id, attendance.class_date
            )
            status, deduct = TeachClassService.resolve_attendance_item(
                page_object.status, page_object.deduct_quantity, leave_map.get(student.id)
            )
            before_remaining = account.remaining_quantity if account else None
            after_remaining = before_remaining
            if deduct > 0:
                account = await TeachClassDao.get_course_account_by_id(
                    query_db, account.id if account else 0, for_update=True
                )
                TeachClassService.check_account_deductible(account, student.student_name, deduct)
                before_remaining, after_remaining = cls.change_account(account, deduct, operator)
            query_db.add(
                TeachClassAttendanceDetail(
                    attendance_id=attendance.id,
                    class_id=class_obj.id,
                    student_id=student.id,
                    student_name=student.student_name,
                    course_account_id=account.id if account else None,
                    status=status,
                    deduct_quantity=deduct,
                    before_remaining=before_remaining,
                    after_remaining=after_remaining,
                    consume_method=member.consume_method if member else '临时学员',
                    is_temp=0 if member else 1,
                    create_by=operator,
                    create_time=datetime.now(),
                    update_by=operator,
                    update_time=datetime.now(),
                    remark=page_object.remark,
                )
            )
            roster.status = TeachClassService.map_class_status_to_schedule(status)
            roster.check_in_time = datetime.now()
            roster.check_in_method = 'M'
            await TeachScheduleAttendanceDao.add_attendance(query_db, roster)
            await cls.recount_attendance(query_db, attendance, operator)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f'已补点名：{cls.STATUS_LABELS.get(status)}，扣课{deduct}',
                result={'eventId': event.id, 'deductQuantity': deduct},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_temp_student_options_services(cls, query_db: AsyncSession, event_id: int, keyword: str | None):
        """
        可加入课次的临时学员：非本班在读、持有本课程有效课程账户、且不在本课次名单中（最多50条）
        """
        event = await cls.get_event(query_db, event_id)
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, event.class_id) if event.class_id else None
        if not class_obj:
            raise ServiceException(message='课次未关联班级')
        roster_rows = await TeachScheduleAttendanceDao.get_attendances_by_event(query_db, event.id)
        roster_ids = {row.student_id for row in roster_rows}
        options = []
        for student, base_user, account in await TeachClassDao.get_available_students(query_db, class_obj, keyword):
            if not account or student.id in roster_ids or account.course_id != event.course_id:
                continue
            options.append(
                {
                    'studentId': student.id,
                    'studentName': student.student_name,
                    'phone': base_user.phone,
                    'courseAccountId': account.id,
                    'courseName': account.course_name,
                    'remainingQuantity': account.remaining_quantity,
                    'unit': account.unit,
                }
            )
            if len(options) >= 50:
                break
        return options

    @classmethod
    async def remove_temp_student_services(cls, query_db: AsyncSession, event_id: int, student_id: int, operator: str):
        event = await cls.get_event(query_db, event_id)
        try:
            if event.class_id:
                await TeachClassDao.get_teach_class_by_id(query_db, event.class_id, for_update=True)
            if await TeachClassDao.get_class_attendance_by_event_id(query_db, event.id, for_update=True):
                raise ServiceException(message='该课次已点名，不能移出学员；如需更正请修改该学员点名')
            row = await TeachLessonDao.get_roster_row(query_db, event.id, student_id)
            if not row or row.is_temp != 1:
                raise ServiceException(message='只能移出临时学员/补课学员')
            row.del_flag = '2'
            row.update_by = operator
            row.update_time = datetime.now()
            event.cached_planned = max((event.cached_planned or 0) - 1, 0)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='已移出本课次')
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 班级：按周重复排课

    @classmethod
    async def weekly_schedule_services(cls, query_db: AsyncSession, page_object: WeeklyScheduleModel, operator: str):
        class_obj = await TeachClassDao.get_teach_class_by_id(query_db, page_object.class_id)
        if not class_obj:
            raise ServiceException(message='班级不存在')
        if class_obj.enroll_status == 3:
            raise ServiceException(message='班级已结课，不能排课')
        teacher_id = page_object.teacher_id or class_obj.teacher_id
        if not teacher_id:
            raise ServiceException(message='请选择上课老师')
        classroom = page_object.classroom if page_object.classroom is not None else class_obj.classroom
        weekdays = set(page_object.weekdays)
        dates = []
        current = page_object.start_date
        while current <= page_object.end_date:
            if current.isoweekday() in weekdays:
                dates.append(current)
            current += timedelta(days=1)
        if not dates:
            raise ServiceException(message='所选日期范围内没有符合的星期')
        if len(dates) > cls.MAX_WEEKLY_EVENTS:
            raise ServiceException(message=f'一次最多生成{cls.MAX_WEEKLY_EVENTS}节课，请缩短日期范围')
        start_clock = datetime.strptime(page_object.start_clock, '%H:%M').time()
        end_clock = datetime.strptime(page_object.end_clock, '%H:%M').time()
        slots = [(datetime.combine(day, start_clock), datetime.combine(day, end_clock)) for day in dates]
        conflicts = []
        course = teacher = None
        for start_time, end_time in slots:
            try:
                _, course, teacher = await TeachScheduleEventService.validate_schedule_base(
                    query_db, class_obj.id, class_obj.course_id, teacher_id, start_time, end_time, classroom
                )
            except ServiceException as e:
                conflicts.append(f'{start_time.strftime("%Y-%m-%d")} {e.message}')
        if conflicts:
            preview = '；'.join(conflicts[:10]) + (f' 等{len(conflicts)}处' if len(conflicts) > 10 else '')
            raise ServiceException(message=f'以下日期存在冲突，未生成任何课次：{preview}')
        student_ids = await TeachScheduleEventService.get_schedule_members(query_db, class_obj.id)
        lesson_hours = TeachScheduleEventService.to_decimal(page_object.lesson_hours, class_obj.lesson_hours or 1)
        try:
            event_ids = []
            for start_time, end_time in slots:
                event_id = await TeachScheduleEventDao.add_teach_schedule_event(
                    query_db,
                    TeachScheduleEvent(
                        teacher_id=teacher.id,
                        course_id=course.id,
                        course_name=course.course_name,
                        class_id=class_obj.id,
                        class_name=class_obj.class_name,
                        subject_code=course.subject,
                        start_time=start_time,
                        end_time=end_time,
                        event_date=start_time.date(),
                        classroom=classroom or class_obj.classroom,
                        lesson_hours=lesson_hours,
                        content=page_object.content,
                        status='0',
                        cached_planned=len(student_ids),
                        create_by=operator,
                        update_by=operator,
                        remark='按周重复排课',
                    ),
                )
                await TeachScheduleEventService.save_event_attendances(query_db, event_id, student_ids, operator)
                event_ids.append(event_id)
            await TeachScheduleEventService.refresh_class_total_lessons(query_db, class_obj.id)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'排课成功，共生成{len(event_ids)}节课', result={'eventIds': event_ids}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 上课记录：修改单个学员点名

    @classmethod
    async def edit_detail_services(cls, query_db: AsyncSession, page_object: EditAttendanceDetailModel, operator: str):
        detail = await TeachLessonDao.get_detail(query_db, page_object.detail_id)
        if not detail:
            raise ServiceException(message='点名明细不存在或已撤销')
        try:
            await TeachClassDao.get_teach_class_by_id(query_db, detail.class_id, for_update=True)
            attendance = await TeachClassDao.get_class_attendance_by_id(query_db, detail.attendance_id, for_update=True)
            if not attendance:
                raise ServiceException(message='点名记录不存在或已撤销')
            detail = await TeachLessonDao.get_detail_for_update(query_db, page_object.detail_id)
            if not detail:
                raise ServiceException(message='点名明细不存在或已撤销')
            if detail.makeup_flag == 1:
                raise ServiceException(message='该缺课记录已标记补课，不能修改点名；请先在补课记录中处理')
            leave_map = await TeachClassService.get_approved_leave_map(
                query_db, attendance.class_id, [detail.student_id], attendance.event_id, attendance.class_date
            )
            new_status, new_deduct = TeachClassService.resolve_attendance_item(
                page_object.status, page_object.deduct_quantity, leave_map.get(detail.student_id)
            )
            old_status, old_deduct = detail.status, detail.deduct_quantity or 0
            delta = new_deduct - old_deduct
            if new_status == old_status and delta == 0 and page_object.remark == detail.remark:
                raise ServiceException(message='点名信息没有变化')
            now = datetime.now()
            if delta != 0:
                if not detail.course_account_id:
                    raise ServiceException(message=f'{detail.student_name}未绑定课程账户，不能扣课')
                account = await TeachClassDao.get_course_account_by_id(
                    query_db, detail.course_account_id, for_update=True
                )
                if not account:
                    raise ServiceException(message=f'{detail.student_name}的课程账户不存在')
                if delta > 0:
                    TeachClassService.check_account_deductible(account, detail.student_name, delta)
                elif account.status not in ('active', 'stopped'):
                    raise ServiceException(message='课程账户已结课/已转出，不能退回课时，请先处理课程账户')
                before, after = cls.change_account(account, delta, operator)
                query_db.add(
                    TeachCourseAccountLog(
                        batch_no=f'AE{now.strftime("%Y%m%d%H%M%S%f")}',
                        op_type='attendance_edit',
                        account_id=account.id,
                        student_id=detail.student_id,
                        student_name=detail.student_name,
                        course_id=account.course_id,
                        course_name=account.course_name,
                        change_quantity=-delta,
                        before_remaining=before,
                        after_remaining=after,
                        before_status=account.status,
                        after_status=account.status,
                        reason=f'修改点名(记录#{attendance.id})：{page_object.reason}'[:200],
                        create_by=operator,
                        create_time=now,
                    )
                )
                detail.after_remaining = after
            note = (
                f'{now.strftime("%m-%d %H:%M")} {operator} 修改点名：{cls.STATUS_LABELS.get(old_status)}/扣{old_deduct}'
                f' → {cls.STATUS_LABELS.get(new_status)}/扣{new_deduct}，原因：{page_object.reason}'
            )
            base_remark = page_object.remark if page_object.remark is not None else detail.remark
            detail.status = new_status
            detail.deduct_quantity = new_deduct
            detail.remark = cls.append_text(base_remark, note)
            detail.update_by = operator
            detail.update_time = now
            if attendance.event_id:
                roster = await TeachLessonDao.get_roster_row(query_db, attendance.event_id, detail.student_id)
                if roster:
                    roster.status = TeachClassService.map_class_status_to_schedule(new_status)
                    roster.update_by = operator
                    roster.update_time = now
                await TeachClassService.sync_makeup_source(
                    query_db, detail.makeup_source_id, attendance.event_id, new_status in (1, 2), operator
                )
            await cls.recount_attendance(query_db, attendance, operator)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='修改成功' + (f'，{"补扣" if delta > 0 else "退回"}课时{abs(delta)}' if delta else ''),
                result={'deltaQuantity': delta},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 上课记录：编辑课次

    @classmethod
    async def edit_record_services(cls, query_db: AsyncSession, page_object: EditAttendanceRecordModel, operator: str):
        attendance = await TeachClassDao.get_class_attendance_by_id(query_db, page_object.id)
        if not attendance:
            raise ServiceException(message='上课记录不存在或已撤销')
        try:
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, attendance.class_id, for_update=True)
            attendance = await TeachClassDao.get_class_attendance_by_id(query_db, page_object.id, for_update=True)
            if not attendance:
                raise ServiceException(message='上课记录不存在或已撤销')
            teacher = None
            if page_object.teacher_id:
                teacher = await TeachClassDao.get_teacher_by_id(query_db, page_object.teacher_id)
                if not teacher:
                    raise ServiceException(message='上课老师不存在')
            old_hours = TeachClassService.to_decimal(attendance.lesson_hours, 1)
            new_hours = TeachClassService.to_decimal(page_object.lesson_hours, 1)
            attendance.class_date = page_object.class_date
            attendance.start_time = page_object.start_time
            attendance.end_time = page_object.end_time
            if teacher:
                attendance.teacher_id = teacher.id
                attendance.teacher_name = teacher.teacher_name
            attendance.classroom = page_object.classroom
            attendance.lesson_hours = new_hours
            attendance.content = page_object.content
            attendance.remark = page_object.remark
            attendance.update_by = operator
            attendance.update_time = datetime.now()
            if class_obj and new_hours != old_hours:
                class_obj.completed_hours = max(
                    TeachClassService.to_decimal(class_obj.completed_hours, 0) + new_hours - old_hours, Decimal('0')
                )
                class_obj.update_by = operator
                class_obj.update_time = datetime.now()
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='修改成功', result={'id': attendance.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------------------------------------------------ 上课记录：开补课班

    @classmethod
    async def makeup_class_services(cls, query_db: AsyncSession, page_object: MakeupClassModel, operator: str):
        detail_ids = sorted(set(page_object.detail_ids))
        try:
            rows = await TeachLessonDao.get_absence_details_with_attendance(query_db, detail_ids)
            if len(rows) != len(detail_ids):
                raise ServiceException(message='部分缺课记录不存在或已撤销，请刷新后重试')
            class_ids = {attendance.class_id for _, attendance in rows}
            if len(class_ids) != 1:
                raise ServiceException(message='一次只能为同一个班级的缺课学员开补课班')
            student_ids = [detail.student_id for detail, _ in rows]
            if len(set(student_ids)) != len(student_ids):
                raise ServiceException(message='同一学员一次只能补一次缺课，请分开开班')
            for detail, _ in rows:
                if detail.status not in (3, 4):
                    raise ServiceException(message=f'{detail.student_name}的记录不是请假/未到，不能补课')
                if detail.makeup_flag == 1:
                    raise ServiceException(message=f'{detail.student_name}的缺课记录已标记已补')
            pending = await TeachLessonDao.get_pending_makeup_rows(query_db, detail_ids)
            if pending:
                names = {detail.id: detail.student_name for detail, _ in rows}
                text = '、'.join(f'{names.get(row[0])}({cls.fmt_time(row[2])})' for row in pending[:5])
                raise ServiceException(message=f'以下缺课已安排补课课次：{text}')
            class_id = class_ids.pop()
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, class_id)
            if not class_obj:
                raise ServiceException(message='班级不存在')
            _, course, teacher = await TeachScheduleEventService.validate_schedule_base(
                query_db,
                class_id,
                class_obj.course_id,
                page_object.teacher_id,
                page_object.start_time,
                page_object.end_time,
                page_object.classroom,
            )
            member_ids = set(await TeachScheduleEventService.get_schedule_members(query_db, class_id))
            roster = []
            for detail, _ in rows:
                if detail.student_id in member_ids:
                    roster.append((detail, None))
                    continue
                account = None
                if detail.course_account_id:
                    account = await TeachClassDao.get_course_account_by_id(query_db, detail.course_account_id)
                    if account and (account.status != 'active' or account.course_id != course.id):
                        account = None
                account = account or await TeachClassDao.get_student_course_account(
                    query_db, detail.student_id, course.id
                )
                if not account:
                    raise ServiceException(
                        message=f'{detail.student_name}已不在本班且没有本课程的有效课程账户，不能加入补课'
                    )
                roster.append((detail, account))
            event_id = await TeachScheduleEventDao.add_teach_schedule_event(
                query_db,
                TeachScheduleEvent(
                    teacher_id=teacher.id,
                    course_id=course.id,
                    course_name=course.course_name,
                    class_id=class_obj.id,
                    class_name=class_obj.class_name,
                    subject_code=course.subject,
                    start_time=page_object.start_time,
                    end_time=page_object.end_time,
                    event_date=page_object.start_time.date(),
                    classroom=page_object.classroom or class_obj.classroom,
                    lesson_hours=TeachScheduleEventService.to_decimal(
                        page_object.lesson_hours, class_obj.lesson_hours or 1
                    ),
                    content=page_object.content or '补课',
                    status='0',
                    event_type='makeup',
                    cached_planned=len(roster),
                    create_by=operator,
                    update_by=operator,
                    remark=f'补课班：来源缺课记录 {",".join(str(i) for i in detail_ids)}'[:500],
                ),
            )
            for detail, account in roster:
                await TeachScheduleAttendanceDao.add_attendance(
                    query_db,
                    TeachScheduleAttendance(
                        event_id=event_id,
                        student_id=detail.student_id,
                        status=0,
                        is_countable=1,
                        is_temp=1 if account else 0,
                        course_account_id=account.id if account else None,
                        makeup_detail_id=detail.id,
                        create_by=operator,
                        update_by=operator,
                    ),
                )
            await TeachScheduleEventService.refresh_class_total_lessons(query_db, class_obj.id)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'补课课次已生成，共{len(roster)}名学员', result={'eventId': event_id}
            )
        except Exception as e:
            await query_db.rollback()
            raise e
