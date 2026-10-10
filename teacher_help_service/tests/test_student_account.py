"""
学员报读课程变更（P3）：批量转课 / 课时清零 / 改有效期 / 停课复课 / 结课，均写操作日志
"""

from datetime import date, timedelta

from tests.helpers import raises_service
from module_teach.entity.do.teach_class_do import TeachClassStudent
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_course_price_do import TeachCoursePrice
from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount
from module_teach.entity.vo.teach_student_account_vo import (
    ChangeCourseValidityModel,
    ClearCourseAccountModel,
    CompleteCourseAccountModel,
    ResumeCourseAccountModel,
    StopCourseAccountModel,
    TeachCourseAccountPageQueryModel,
    TransferCourseAccountModel,
)
from module_teach.service.teach_student_account_service import TeachStudentAccountService


async def make_course(factory, name, charge_type='class'):
    course = await factory.add(TeachCourse(course_name=name, status=1, del_flag=0))
    await factory.add(TeachCoursePrice(course_id=course.id, charge_type=charge_type, price_name='单价'))
    return course


async def reload(db, model, pk):
    return await db.get(model, pk, populate_existing=True)


async def test_transfer_moves_all_remaining_and_logs(db, factory):
    src_course = await make_course(factory, '数学')
    dst_course = await make_course(factory, '英语')
    student = await factory.student('转课学员')
    account = await factory.course_account(student, 10, course_id=src_course.id)
    account.charge_type = 'class'
    account.unit = '课时'
    account.valid_end_date = date(2027, 1, 1)
    class_obj = await factory.class_with_students([(student, account)])
    await db.commit()

    form = TransferCourseAccountModel(accountIds=[account.id], targetCourseId=dst_course.id, reason='家长要求')
    result = await TeachStudentAccountService.transfer_services(db, form, 'tester')
    assert result.is_success
    old = await reload(db, TeachStudentCourseAccount, account.id)
    assert old.remaining_quantity == 0 and old.transferred_quantity == 10 and old.status == 'transferred'
    new_id = result.result['items'][0]['toAccountId']
    new = await reload(db, TeachStudentCourseAccount, new_id)
    assert new.course_id == dst_course.id and new.remaining_quantity == 10 and new.valid_end_date == date(2027, 1, 1)
    member = (
        await db.execute(TeachClassStudent.__table__.select().where(TeachClassStudent.class_id == class_obj.id))
    ).first()
    assert member.status == 2
    logs = await TeachStudentAccountService.get_account_logs_services(db, student.id, None)
    assert {log['opType'] for log in logs} == {'transfer_out', 'transfer_in'}

    with raises_service('不能转课'):
        await TeachStudentAccountService.transfer_services(db, form, 'tester')


async def test_transfer_rejects_same_course_and_charge_mismatch(db, factory):
    course = await make_course(factory, '数学')
    month_course = await make_course(factory, '托管', charge_type='month')
    student = await factory.student('学员')
    account = await factory.course_account(student, 5, course_id=course.id)
    account.charge_type = 'class'
    await db.commit()
    account_id, course_id, month_course_id = account.id, course.id, month_course.id
    with raises_service('相同'):
        await TeachStudentAccountService.transfer_services(
            db, TransferCourseAccountModel(accountIds=[account_id], targetCourseId=course_id), 'tester'
        )
    with raises_service('收费方式'):
        await TeachStudentAccountService.transfer_services(
            db, TransferCourseAccountModel(accountIds=[account_id], targetCourseId=month_course_id), 'tester'
        )
    assert (await reload(db, TeachStudentCourseAccount, account_id)).remaining_quantity == 5


async def test_clear_validity_stop_resume_complete(db, factory):
    student = await factory.student('学员乙')
    account = await factory.course_account(student, 8)
    account.valid_end_date = date(2027, 1, 10)
    other = await factory.course_account(student, 3)
    class_obj = await factory.class_with_students([(student, other)])
    await db.commit()
    account_id, other_id, class_id, student_id = account.id, other.id, class_obj.id, student.id

    await TeachStudentAccountService.change_validity_services(
        db, ChangeCourseValidityModel(accountIds=[account_id], validEndDate=date(2027, 2, 1)), 'tester'
    )
    assert (await reload(db, TeachStudentCourseAccount, account_id)).valid_end_date == date(2027, 2, 1)

    stop_day = date.today() - timedelta(days=5)
    await TeachStudentAccountService.stop_services(
        db, StopCourseAccountModel(accountIds=[account_id], stopDate=stop_day, reason='生病'), 'tester'
    )
    stopped = await reload(db, TeachStudentCourseAccount, account_id)
    assert stopped.status == 'stopped' and stopped.stop_date == stop_day
    with raises_service('不能停课'):
        await TeachStudentAccountService.stop_services(
            db, StopCourseAccountModel(accountIds=[account_id], stopDate=stop_day, reason='再停'), 'tester'
        )

    await TeachStudentAccountService.resume_services(db, ResumeCourseAccountModel(accountIds=[account_id]), 'tester')
    resumed = await reload(db, TeachStudentCourseAccount, account_id)
    assert resumed.status == 'active' and resumed.valid_end_date == date(2027, 2, 6) and resumed.stop_date is None

    result = await TeachStudentAccountService.clear_services(
        db, ClearCourseAccountModel(accountIds=[account_id], reason='过期清零'), 'tester'
    )
    assert result.result['clearedQuantity'] == 8
    cleared = await reload(db, TeachStudentCourseAccount, account_id)
    assert cleared.remaining_quantity == 0 and cleared.cleared_quantity == 8 and cleared.status == 'active'

    await TeachStudentAccountService.complete_services(db, CompleteCourseAccountModel(accountIds=[other_id]), 'tester')
    completed = await reload(db, TeachStudentCourseAccount, other_id)
    assert completed.status == 'completed' and completed.remaining_quantity == 0 and completed.cleared_quantity == 3
    member = (
        await db.execute(TeachClassStudent.__table__.select().where(TeachClassStudent.class_id == class_id))
    ).first()
    assert member.status == 2
    with raises_service('不能结课'):
        await TeachStudentAccountService.complete_services(
            db, CompleteCourseAccountModel(accountIds=[other_id]), 'tester'
        )

    ops = [log['opType'] for log in await TeachStudentAccountService.get_account_logs_services(db, student_id, None)]
    assert sorted(ops) == sorted(['validity', 'stop', 'resume', 'clear', 'complete'])

    page = await TeachStudentAccountService.get_account_list_services(
        db, TeachCourseAccountPageQueryModel(studentName='学员乙', status='completed')
    )
    assert page.total == 1 and page.rows[0]['statusName'] == '结课'


async def test_missing_account_and_logs_need_scope(db, factory):
    with raises_service('不存在'):
        await TeachStudentAccountService.clear_services(
            db, ClearCourseAccountModel(accountIds=[987654], reason='x'), 'tester'
        )
    with raises_service('请指定'):
        await TeachStudentAccountService.get_account_logs_services(db, None, None)
