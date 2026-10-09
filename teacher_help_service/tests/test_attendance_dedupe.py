"""
点名判重（P0）：同一课次只能点名一次；扣课不超过剩余课时
"""

from datetime import date


from tests.helpers import raises_service
from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount
from module_teach.entity.vo.teach_class_vo import SubmitTeachClassAttendanceModel
from module_teach.service.teach_class_service import TeachClassService


def roll_call(event_id, details):
    return SubmitTeachClassAttendanceModel(
        event_id=event_id,
        class_date=date.today(),
        start_time='09:00',
        end_time='10:00',
        details=details,
    )


async def setup_class(db, factory, remaining=5):
    student = await factory.student('张三')
    account = await factory.course_account(student, remaining)
    class_obj = await factory.class_with_students([(student, account)])
    event = await factory.event(class_obj, [student.id])
    ids = (student.id, account.id, class_obj.id, event.id)
    await db.commit()
    return ids


async def test_same_event_cannot_roll_call_twice(db, factory):
    student_id, account_id, class_id, event_id = await setup_class(db, factory)
    details = [{'studentId': student_id, 'status': 1, 'deductQuantity': 1}]
    result = await TeachClassService.submit_class_attendance_services(
        db, class_id, roll_call(event_id, details), 'tester'
    )
    assert result.is_success
    with raises_service('已完成点名'):
        await TeachClassService.submit_class_attendance_services(db, class_id, roll_call(event_id, details), 'tester')
    refreshed = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert refreshed.remaining_quantity == 4
    assert refreshed.consumed_quantity == 1


async def test_deduct_more_than_remaining_rejected(db, factory):
    student_id, account_id, class_id, event_id = await setup_class(db, factory, remaining=1)
    details = [{'studentId': student_id, 'status': 1, 'deductQuantity': 2}]
    with raises_service('剩余课时不足'):
        await TeachClassService.submit_class_attendance_services(db, class_id, roll_call(event_id, details), 'tester')
    refreshed = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert refreshed.remaining_quantity == 1


async def test_duplicate_student_in_one_submit_rejected(db, factory):
    student_id, _, class_id, event_id = await setup_class(db, factory)
    details = [
        {'studentId': student_id, 'status': 1, 'deductQuantity': 1},
        {'studentId': student_id, 'status': 1, 'deductQuantity': 1},
    ]
    with raises_service('重复'):
        await TeachClassService.submit_class_attendance_services(db, class_id, roll_call(event_id, details), 'tester')
