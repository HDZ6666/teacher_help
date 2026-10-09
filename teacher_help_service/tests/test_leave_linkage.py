"""
请假联动（P1）：已通过请假在点名时记为请假、按 is_deduct 决定是否扣课；审批同步课表考勤
"""

from datetime import date

from module_teach.entity.do.teach_class_do import TeachClassAttendance, TeachClassAttendanceDetail
from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount
from module_teach.entity.do.teach_leave_do import TeachLeaveApplication
from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
from module_teach.entity.vo.teach_class_vo import SubmitTeachClassAttendanceModel
from module_teach.entity.vo.teach_leave_vo import ApproveTeachLeaveModel, DeleteTeachLeaveModel
from module_teach.service.teach_class_service import TeachClassService
from module_teach.service.teach_leave_service import TeachLeaveService
from sqlalchemy import select


def test_resolve_attendance_item_rules():
    approved_no_deduct = TeachLeaveApplication(is_deduct=0)
    approved_deduct = TeachLeaveApplication(is_deduct=1)
    # 无请假：到课按提交扣，请假/未到不扣
    assert TeachClassService.resolve_attendance_item(1, 1) == (1, 1)
    assert TeachClassService.resolve_attendance_item(3, 1) == (3, 0)
    assert TeachClassService.resolve_attendance_item(4, 1) == (4, 0)
    # 已通过请假：未到 -> 请假；不扣课时的请假不扣
    assert TeachClassService.resolve_attendance_item(4, 1, approved_no_deduct) == (3, 0)
    assert TeachClassService.resolve_attendance_item(3, 1, approved_no_deduct) == (3, 0)
    # 请假单标记扣课时：按提交数量扣
    assert TeachClassService.resolve_attendance_item(3, 1, approved_deduct) == (3, 1)
    # 请了假但实际到课：按到课处理
    assert TeachClassService.resolve_attendance_item(1, 1, approved_no_deduct) == (1, 1)


async def setup(db, factory):
    student = await factory.student('李四')
    account = await factory.course_account(student, 5)
    class_obj = await factory.class_with_students([(student, account)])
    event = await factory.event(class_obj, [student.id])
    leave = TeachLeaveApplication(
        leave_no='LV-TEST-1',
        student_id=student.id,
        student_name=student.student_name,
        class_id=class_obj.id,
        event_id=event.id,
        leave_date=event.event_date,
        is_deduct=0,
        leave_status=1,
    )
    db.add(leave)
    await db.flush()
    ids = (student.id, account.id, class_obj.id, event.id, leave.id)
    await db.commit()
    return ids


async def schedule_status(db, event_id, student_id):
    result = await db.execute(
        select(TeachScheduleAttendance.status).where(
            TeachScheduleAttendance.event_id == event_id, TeachScheduleAttendance.student_id == student_id
        )
    )
    return result.scalar()


async def test_approve_before_roll_call_marks_leave_and_no_deduction(db, factory):
    student_id, account_id, class_id, event_id, leave_id = await setup(db, factory)
    await TeachLeaveService.approve_leave_services(db, ApproveTeachLeaveModel(id=leave_id, leaveStatus=2), 'op')
    assert await schedule_status(db, event_id, student_id) == 3

    prepare = await TeachClassService.get_attendance_prepare_services(db, class_id, event_id)
    row = prepare['students'][0]
    assert (row['attendanceStatus'], row['deductQuantity'], row['leaveId']) == (3, 0, leave_id)

    # 操作员误提交“未到 + 扣 1 课时”，后端按已通过请假更正为请假且不扣课
    model = SubmitTeachClassAttendanceModel(
        event_id=event_id,
        class_date=date.today(),
        start_time='09:00',
        end_time='10:00',
        details=[{'studentId': student_id, 'status': 4, 'deductQuantity': 1}],
    )
    await TeachClassService.submit_class_attendance_services(db, class_id, model, 'op')
    detail = (await db.execute(select(TeachClassAttendanceDetail))).scalars().first()
    assert (detail.status, detail.deduct_quantity) == (3, 0)
    refreshed = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert refreshed.remaining_quantity == 5


async def test_approve_after_roll_call_corrects_absent(db, factory):
    student_id, _, class_id, event_id, leave_id = await setup(db, factory)
    model = SubmitTeachClassAttendanceModel(
        event_id=event_id,
        class_date=date.today(),
        start_time='09:00',
        end_time='10:00',
        details=[{'studentId': student_id, 'status': 4, 'deductQuantity': 0}],
    )
    await TeachClassService.submit_class_attendance_services(db, class_id, model, 'op')
    await TeachLeaveService.approve_leave_services(db, ApproveTeachLeaveModel(id=leave_id, leaveStatus=2), 'op')
    attendance = (await db.execute(select(TeachClassAttendance))).scalars().first()
    await db.refresh(attendance)
    assert (attendance.absent_count, attendance.leave_count) == (0, 1)
    detail = (await db.execute(select(TeachClassAttendanceDetail))).scalars().first()
    await db.refresh(detail)
    assert detail.status == 3
    assert await schedule_status(db, event_id, student_id) == 3


async def test_revoke_approved_leave_before_roll_call_restores_pending(db, factory):
    student_id, _, _, event_id, leave_id = await setup(db, factory)
    await TeachLeaveService.approve_leave_services(db, ApproveTeachLeaveModel(id=leave_id, leaveStatus=2), 'op')
    await TeachLeaveService.delete_leave_services(db, DeleteTeachLeaveModel(leave_ids=str(leave_id)), 'op')
    assert await schedule_status(db, event_id, student_id) == 0


async def test_rejected_leave_has_no_effect(db, factory):
    student_id, _, _, event_id, leave_id = await setup(db, factory)
    await TeachLeaveService.approve_leave_services(db, ApproveTeachLeaveModel(id=leave_id, leaveStatus=3), 'op')
    assert await schedule_status(db, event_id, student_id) == 0
