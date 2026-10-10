"""
上课记录导出（P2）：按查询条件导出点名记录/补课记录 Excel
"""

import io

import pandas as pd

from tests.helpers import raises_service
from tests.test_attendance_dedupe import roll_call, setup_class
from module_teach.entity.vo.teach_class_record_vo import (
    ClassRecordAttendanceQueryModel,
    ClassRecordMakeupQueryModel,
    ClassRecordOvertimeQueryModel,
)
from module_teach.service.teach_class_record_service import TeachClassRecordService
from module_teach.service.teach_class_service import TeachClassService


async def test_export_attendance_and_makeup(db, factory):
    student_id, _, class_id, event_id = await setup_class(db, factory, remaining=5)
    details = [{'studentId': student_id, 'status': 4, 'deductQuantity': 1}]
    await TeachClassService.submit_class_attendance_services(db, class_id, roll_call(event_id, details), 'tester')

    data = await TeachClassRecordService.export_record_list_services(
        db, 'attendance', ClassRecordAttendanceQueryModel(classId=class_id, pageSize=1)
    )
    df = pd.read_excel(io.BytesIO(data))
    assert len(df) == 1 and '班级名称' in df.columns and '扣课合计' in df.columns

    data = await TeachClassRecordService.export_record_list_services(
        db, 'makeup', ClassRecordMakeupQueryModel(classId=class_id)
    )
    df = pd.read_excel(io.BytesIO(data))
    assert len(df) == 1 and df.iloc[0]['缺课状态'] == '未到'


async def test_export_rejects_unknown_type(db):
    with raises_service('不支持'):
        await TeachClassRecordService.export_record_list_services(db, 'foo', ClassRecordOvertimeQueryModel())


async def test_mark_makeup_is_flag_only_and_idempotent(db, factory):
    from module_teach.entity.do.teach_class_do import TeachClassAttendanceDetail
    from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount

    student_id, account_id, class_id, event_id = await setup_class(db, factory, remaining=5)
    details = [{'studentId': student_id, 'status': 4, 'deductQuantity': 1}]
    await TeachClassService.submit_class_attendance_services(db, class_id, roll_call(event_id, details), 'tester')
    page = await TeachClassRecordService.get_makeup_list_services(db, ClassRecordMakeupQueryModel(classId=class_id))
    detail_id = page.rows[0]['id']
    assert page.rows[0]['madeupStatus'] is False
    before = (await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)).remaining_quantity

    result = await TeachClassRecordService.mark_makeup_services(db, [detail_id], '周六补', 'tester')
    assert result.result == {'marked': 1, 'skipped': 0}
    again = await TeachClassRecordService.mark_makeup_services(db, [detail_id], None, 'tester')
    assert again.result == {'marked': 0, 'skipped': 1}
    detail = await db.get(TeachClassAttendanceDetail, detail_id, populate_existing=True)
    assert detail.makeup_flag == 1 and detail.makeup_remark == '周六补' and detail.status == 4
    account = await db.get(TeachStudentCourseAccount, account_id, populate_existing=True)
    assert account.remaining_quantity == before

    pending = await TeachClassRecordService.get_makeup_list_services(
        db, ClassRecordMakeupQueryModel(classId=class_id, makeupFlag=0)
    )
    assert pending.total == 0
    with raises_service('不存在'):
        await TeachClassRecordService.mark_makeup_services(db, [999999], None, 'tester')


async def test_mark_makeup_rejects_present_student(db, factory):
    from module_teach.entity.do.teach_class_do import TeachClassAttendanceDetail

    student_id, _, class_id, event_id = await setup_class(db, factory, remaining=5)
    details = [{'studentId': student_id, 'status': 1, 'deductQuantity': 1}]
    await TeachClassService.submit_class_attendance_services(db, class_id, roll_call(event_id, details), 'tester')
    detail = (await db.execute(TeachClassAttendanceDetail.__table__.select())).first()
    with raises_service('无需补课'):
        await TeachClassRecordService.mark_makeup_services(db, [detail.id], None, 'tester')
