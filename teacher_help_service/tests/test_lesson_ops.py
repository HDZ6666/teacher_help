"""
P3 第二批课次操作：课表调课、临时学员、按周重复排课、修改单个学员点名、编辑课次、开补课班
"""

from datetime import date, datetime, timedelta

from tests.helpers import raises_service
from tests.test_attendance_dedupe import roll_call
from module_teach.entity.do.teach_class_do import TeachClass, TeachClassAttendance, TeachClassAttendanceDetail
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_enrollment_order_do import TeachCourseAccountLog, TeachStudentCourseAccount
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
from module_teach.service.teach_lesson_service import TeachLessonService


async def setup(db, factory, remaining=5):
    """
    一门课程、一个班（学员张三在读）、一节课次；另有非本班学员李四持有同课程账户
    """
    course = await factory.add(TeachCourse(id=1, course_name='测试课程', status=1, del_flag=0))
    student = await factory.student('张三')
    account = await factory.course_account(student, remaining, course_id=course.id)
    class_obj = await factory.class_with_students([(student, account)])
    event = await factory.event(class_obj, [student.id], event_date=date.today() + timedelta(days=1))
    other = await factory.student('李四')
    other_account = await factory.course_account(other, remaining, course_id=course.id)
    await db.commit()
    return {
        'student': student.id,
        'account': account.id,
        'class': class_obj.id,
        'event': event.id,
        'teacher': event.teacher_id,
        'other': other.id,
        'other_account': other_account.id,
        'start': event.start_time,
    }


async def remaining(db, account_id):
    account = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    return account.remaining_quantity


async def test_reschedule_and_conflict(db, factory):
    ids = await setup(db, factory)
    new_start = ids['start'] + timedelta(days=1, hours=2)
    result = await TeachLessonService.reschedule_services(
        db,
        RescheduleLessonModel(
            event_id=ids['event'], start_time=new_start, end_time=new_start + timedelta(hours=1),
            classroom='A101', reason='老师请假',
        ),
        'tester',
    )
    assert result.is_success
    event = await db.get(TeachScheduleEvent, ids['event'], populate_existing=True)
    assert event.start_time == new_start and event.classroom == 'A101' and '调课' in event.remark
    # 同老师同时间另建一节课 -> 调课冲突
    db.add(
        TeachScheduleEvent(
            teacher_id=ids['teacher'], class_id=None, start_time=ids['start'],
            end_time=ids['start'] + timedelta(hours=1), event_date=ids['start'].date(), status='0', del_flag='0',
        )
    )
    await db.commit()
    with raises_service('冲突'):
        await TeachLessonService.reschedule_services(
            db,
            RescheduleLessonModel(
                event_id=ids['event'], start_time=ids['start'], end_time=ids['start'] + timedelta(hours=1)
            ),
            'tester',
        )
    # 已点名课次不能调课
    await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(ids['event'], [{'studentId': ids['student'], 'status': 1, 'deductQuantity': 1}]),
        'tester',
    )
    with raises_service('未点名'):
        await TeachLessonService.reschedule_services(
            db,
            RescheduleLessonModel(event_id=ids['event'], start_time=new_start, end_time=new_start + timedelta(hours=1)),
            'tester',
        )


async def test_temp_student_before_and_after_roll_call(db, factory):
    ids = await setup(db, factory)
    options = await TeachLessonService.get_temp_student_options_services(db, ids['event'], None)
    assert [item['studentId'] for item in options] == [ids['other']]
    await TeachLessonService.add_temp_student_services(
        db, AddTempStudentModel(event_id=ids['event'], student_id=ids['other']), 'tester'
    )
    with raises_service('已在本课次名单'):
        await TeachLessonService.add_temp_student_services(
            db, AddTempStudentModel(event_id=ids['event'], student_id=ids['other']), 'tester'
        )
    prepare = await TeachClassService.get_attendance_prepare_services(db, ids['class'], ids['event'])
    temp_rows = [row for row in prepare['students'] if row['isTemp'] == 1]
    assert len(temp_rows) == 1 and temp_rows[0]['courseAccountId'] == ids['other_account']
    details = [
        {'studentId': ids['student'], 'status': 1, 'deductQuantity': 1},
        {'studentId': ids['other'], 'status': 1, 'deductQuantity': 1},
    ]
    result = await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(ids['event'], details), 'tester'
    )
    assert await remaining(db, ids['other_account']) == 4
    detail = (
        await db.execute(
            TeachClassAttendanceDetail.__table__.select().where(TeachClassAttendanceDetail.student_id == ids['other'])
        )
    ).first()
    assert detail.is_temp == 1
    # 已点名课次再加临时学员：直接补点名扣课
    third = await factory.student('王五')
    third_account = await factory.course_account(third, 3, course_id=1)
    third_id, third_account_id = third.id, third_account.id
    await db.commit()
    with raises_service('请选择到课状态'):
        await TeachLessonService.add_temp_student_services(
            db, AddTempStudentModel(event_id=ids['event'], student_id=third_id), 'tester'
        )
    await TeachLessonService.add_temp_student_services(
        db, AddTempStudentModel(event_id=ids['event'], student_id=third_id, status=2, deduct_quantity=1), 'tester'
    )
    assert await remaining(db, third_account_id) == 2
    attendance = await db.get(TeachClassAttendance, result.result['id'], populate_existing=True)
    assert (attendance.student_count, attendance.present_count, attendance.late_count) == (3, 2, 1)
    assert attendance.deducted_quantity == 3
    # 撤销点名也会退回临时学员课时
    await TeachClassService.revoke_class_attendance_services(db, attendance.id, '测试', 'tester')
    assert await remaining(db, third_account_id) == 3
    assert await remaining(db, ids['other_account']) == 5


async def test_temp_student_requires_active_account(db, factory):
    ids = await setup(db, factory)
    stranger = await factory.student('赵六')
    await db.commit()
    with raises_service('没有本课程的有效课程账户'):
        await TeachLessonService.add_temp_student_services(
            db, AddTempStudentModel(event_id=ids['event'], student_id=stranger.id), 'tester'
        )
    account = await db.get(TeachStudentCourseAccount, ids['other_account'])
    account.status = 'stopped'
    await db.commit()
    with raises_service('不是有效状态'):
        await TeachLessonService.add_temp_student_services(
            db,
            AddTempStudentModel(event_id=ids['event'], student_id=ids['other'], course_account_id=ids['other_account']),
            'tester',
        )


async def test_stopped_account_cannot_be_deducted(db, factory):
    ids = await setup(db, factory)
    account = await db.get(TeachStudentCourseAccount, ids['account'])
    account.status = 'stopped'
    await db.commit()
    details = [{'studentId': ids['student'], 'status': 1, 'deductQuantity': 1}]
    with raises_service('不是有效状态'):
        await TeachClassService.submit_class_attendance_services(
            db, ids['class'], roll_call(ids['event'], details), 'tester'
        )


async def test_weekly_schedule_all_or_nothing(db, factory):
    ids = await setup(db, factory)
    class_obj = await db.get(TeachClass, ids['class'])
    class_obj.teacher_id = ids['teacher']
    await db.commit()
    start = date.today() + timedelta(days=7)
    form = WeeklyScheduleModel(
        class_id=ids['class'], start_date=start, end_date=start + timedelta(days=13),
        weekdays=[start.isoweekday()], start_clock='18:00', end_clock='19:00',
    )
    result = await TeachLessonService.weekly_schedule_services(db, form, 'tester')
    assert len(result.result['eventIds']) == 2
    rows = (
        await db.execute(
            TeachScheduleAttendance.__table__.select().where(
                TeachScheduleAttendance.event_id.in_(result.result['eventIds'])
            )
        )
    ).all()
    assert len(rows) == 2
    # 再排一次同样时间 -> 全部冲突，不生成任何课次
    with raises_service('未生成任何课次'):
        await TeachLessonService.weekly_schedule_services(db, form, 'tester')
    class_obj = await db.get(TeachClass, ids['class'], populate_existing=True)
    assert class_obj.total_lessons == 3


async def test_edit_detail_refund_and_rededuct(db, factory):
    ids = await setup(db, factory, remaining=5)
    result = await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(ids['event'], [{'studentId': ids['student'], 'status': 1, 'deductQuantity': 2}]),
        'tester',
    )
    detail = (
        await db.execute(
            TeachClassAttendanceDetail.__table__.select().where(
                TeachClassAttendanceDetail.attendance_id == result.result['id']
            )
        )
    ).first()
    # 到课扣2 -> 未到：退回2
    edited = await TeachLessonService.edit_detail_services(
        db, EditAttendanceDetailModel(detail_id=detail.id, status=4, deduct_quantity=2, reason='点错'), 'tester'
    )
    assert edited.result['deltaQuantity'] == -2
    assert await remaining(db, ids['account']) == 5
    attendance = await db.get(TeachClassAttendance, result.result['id'], populate_existing=True)
    assert (attendance.present_count, attendance.absent_count, attendance.deducted_quantity) == (0, 1, 0)
    roster = (
        await db.execute(
            TeachScheduleAttendance.__table__.select().where(TeachScheduleAttendance.event_id == ids['event'])
        )
    ).first()
    assert roster.status == 4
    # 未到 -> 迟到扣1：补扣1，写课程账户日志
    await TeachLessonService.edit_detail_services(
        db, EditAttendanceDetailModel(detail_id=detail.id, status=2, deduct_quantity=1, reason='实际迟到'), 'tester'
    )
    assert await remaining(db, ids['account']) == 4
    logs = (await db.execute(TeachCourseAccountLog.__table__.select())).all()
    assert [log.change_quantity for log in logs] == [2, -1]
    with raises_service('剩余课时不足'):
        await TeachLessonService.edit_detail_services(
            db, EditAttendanceDetailModel(detail_id=detail.id, status=1, deduct_quantity=9, reason='x'), 'tester'
        )


async def test_edit_record_adjusts_completed_hours(db, factory):
    ids = await setup(db, factory)
    result = await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(ids['event'], [{'studentId': ids['student'], 'status': 1, 'deductQuantity': 1}]),
        'tester',
    )
    await TeachLessonService.edit_record_services(
        db,
        EditAttendanceRecordModel(
            id=result.result['id'], class_date=date.today(), start_time='10:00', end_time='12:00',
            lesson_hours=2, content='第一单元', classroom='B2',
        ),
        'tester',
    )
    attendance = await db.get(TeachClassAttendance, result.result['id'], populate_existing=True)
    assert (attendance.start_time, attendance.content, attendance.classroom) == ('10:00', '第一单元', 'B2')
    class_obj = await db.get(TeachClass, ids['class'], populate_existing=True)
    assert float(class_obj.completed_hours) == 2.0


async def test_makeup_class_marks_source_after_roll_call(db, factory):
    ids = await setup(db, factory)
    first = await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(ids['event'], [{'studentId': ids['student'], 'status': 4, 'deductQuantity': 0}]),
        'tester',
    )
    detail = (
        await db.execute(
            TeachClassAttendanceDetail.__table__.select().where(
                TeachClassAttendanceDetail.attendance_id == first.result['id']
            )
        )
    ).first()
    start = datetime.combine(date.today() + timedelta(days=3), datetime.min.time()) + timedelta(hours=15)
    form = MakeupClassModel(
        detail_ids=[detail.id], start_time=start, end_time=start + timedelta(hours=1), teacher_id=ids['teacher']
    )
    made = await TeachLessonService.makeup_class_services(db, form, 'tester')
    makeup_event_id = made.result['eventId']
    event = await db.get(TeachScheduleEvent, makeup_event_id)
    assert event.event_type == 'makeup'
    later = start + timedelta(hours=3)
    with raises_service('已安排补课课次'):
        await TeachLessonService.makeup_class_services(
            db,
            MakeupClassModel(
                detail_ids=[detail.id], start_time=later, end_time=later + timedelta(hours=1), teacher_id=ids['teacher']
            ),
            'tester',
        )
    second = await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(makeup_event_id, [{'studentId': ids['student'], 'status': 1, 'deductQuantity': 1}]),
        'tester',
    )
    source = await db.get(TeachClassAttendanceDetail, detail.id, populate_existing=True)
    assert source.makeup_flag == 1 and source.makeup_remark.startswith(f'补课课次#{makeup_event_id}')
    with raises_service('已标记补课'):
        await TeachLessonService.edit_detail_services(
            db, EditAttendanceDetailModel(detail_id=detail.id, status=1, deduct_quantity=1, reason='x'), 'tester'
        )
    # 撤销补课课次点名 -> 取消已补标记
    await TeachClassService.revoke_class_attendance_services(db, second.result['id'], None, 'tester')
    source = await db.get(TeachClassAttendanceDetail, detail.id, populate_existing=True)
    assert source.makeup_flag == 0


async def test_makeup_class_rejects_present_record(db, factory):
    ids = await setup(db, factory)
    first = await TeachClassService.submit_class_attendance_services(
        db, ids['class'], roll_call(ids['event'], [{'studentId': ids['student'], 'status': 1, 'deductQuantity': 1}]),
        'tester',
    )
    detail = (
        await db.execute(
            TeachClassAttendanceDetail.__table__.select().where(
                TeachClassAttendanceDetail.attendance_id == first.result['id']
            )
        )
    ).first()
    start = datetime.combine(date.today() + timedelta(days=3), datetime.min.time()) + timedelta(hours=15)
    with raises_service('不是请假/未到'):
        await TeachLessonService.makeup_class_services(
            db,
            MakeupClassModel(
                detail_ids=[detail.id], start_time=start, end_time=start + timedelta(hours=1), teacher_id=ids['teacher']
            ),
            'tester',
        )
