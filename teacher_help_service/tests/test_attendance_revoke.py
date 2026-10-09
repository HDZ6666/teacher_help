"""
撤销点名（P2）：退回课时、释放课次可重新点名、课表考勤恢复、已有点评不能撤销
"""

from tests.helpers import raises_service
from tests.test_attendance_dedupe import roll_call, setup_class
from module_teach.entity.do.teach_class_do import TeachClass, TeachClassAttendance
from module_teach.entity.do.teach_comment_do import TeachStudentComment
from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent
from module_teach.service.teach_class_service import TeachClassService


async def test_revoke_refunds_and_allows_roll_call_again(db, factory):
    student_id, account_id, class_id, event_id = await setup_class(db, factory, remaining=5)
    details = [{'studentId': student_id, 'status': 1, 'deductQuantity': 2}]
    result = await TeachClassService.submit_class_attendance_services(
        db, class_id, roll_call(event_id, details), 'tester'
    )
    attendance_id = result.result['id']
    account = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert account.remaining_quantity == 3

    revoked = await TeachClassService.revoke_class_attendance_services(db, attendance_id, '点错了', 'tester')
    assert revoked.result['refundedQuantity'] == 2
    account = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert (account.remaining_quantity, account.consumed_quantity) == (5, 0)
    attendance = await db.get(TeachClassAttendance, attendance_id, populate_existing=True)
    assert attendance.del_flag == 1 and attendance.event_id is None and '点错了' in attendance.remark
    class_obj = await db.get(TeachClass, class_id, populate_existing=True)
    assert class_obj.completed_lessons == 0
    event = await db.get(TeachScheduleEvent, event_id, populate_existing=True)
    assert event.status == '0'
    schedule_row = (
        await db.execute(TeachScheduleAttendance.__table__.select().where(TeachScheduleAttendance.event_id == event_id))
    ).first()
    assert schedule_row.status == 0 and schedule_row.check_in_time is None

    with raises_service('已撤销'):
        await TeachClassService.revoke_class_attendance_services(db, attendance_id, None, 'tester')
    # 课次可以重新点名
    again = await TeachClassService.submit_class_attendance_services(
        db, class_id, roll_call(event_id, [{'studentId': student_id, 'status': 1, 'deductQuantity': 1}]), 'tester'
    )
    assert again.is_success
    account = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert account.remaining_quantity == 4


async def test_revoke_blocked_when_commented(db, factory):
    student_id, _, class_id, event_id = await setup_class(db, factory)
    details = [{'studentId': student_id, 'status': 1, 'deductQuantity': 1}]
    result = await TeachClassService.submit_class_attendance_services(
        db, class_id, roll_call(event_id, details), 'tester'
    )
    db.add(TeachStudentComment(attendance_id=result.result['id'], student_id=student_id, del_flag=0))
    await db.commit()
    with raises_service('课后点评'):
        await TeachClassService.revoke_class_attendance_services(db, result.result['id'], None, 'tester')
