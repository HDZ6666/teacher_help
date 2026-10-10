"""
老师课时统计（P2）：按点名记录汇总上月/本月/累计课时，已撤销的点名不计入
"""

from datetime import date, timedelta
from decimal import Decimal

from module_teach.entity.do.teach_class_do import TeachClass, TeachClassAttendance
from module_teach.service.teach_teacher_stat_service import TeachTeacherStatService


async def add_attendance(db, teacher_id, class_id, class_date, hours, del_flag=0):
    db.add(
        TeachClassAttendance(
            class_id=class_id,
            class_name='测试班',
            course_id=1,
            course_name='测试课程',
            teacher_id=teacher_id,
            class_date=class_date,
            start_time='09:00',
            end_time='10:00',
            lesson_hours=Decimal(str(hours)),
            student_count=2,
            present_count=1,
            del_flag=del_flag,
        )
    )
    await db.flush()


async def test_teacher_stats_by_month(db, factory):
    teacher = await factory.teacher('李老师')
    other = await factory.teacher('赵老师')
    class_obj = await factory.add(
        TeachClass(class_name='测试班', course_id=1, course_name='测试课程', teacher_id=teacher.id)
    )
    today = date(2026, 10, 15)
    await add_attendance(db, teacher.id, class_obj.id, date(2026, 10, 2), 2)
    await add_attendance(db, teacher.id, class_obj.id, date(2026, 10, 9), 1.5)
    await add_attendance(db, teacher.id, class_obj.id, date(2026, 9, 20), 2)
    await add_attendance(db, teacher.id, class_obj.id, date(2026, 8, 1), 1)
    await add_attendance(db, teacher.id, class_obj.id, date(2026, 10, 10), 3, del_flag=1)
    await db.commit()

    rows = await TeachTeacherStatService.get_teacher_stats_services(db, [teacher.id, other.id], today)
    stat = next(row for row in rows if row['teacherId'] == teacher.id)
    assert (stat['thisMonthLessons'], stat['thisMonthHours']) == (2, 3.5)
    assert (stat['lastMonthLessons'], stat['lastMonthHours']) == (1, 2)
    assert (stat['totalLessons'], stat['totalHours']) == (4, 6.5)
    assert stat['classCount'] == 1
    empty = next(row for row in rows if row['teacherId'] == other.id)
    assert empty['totalLessons'] == 0 and empty['classCount'] == 0


async def test_teacher_records_page(db, factory):
    teacher = await factory.teacher('钱老师')
    class_obj = await factory.add(TeachClass(class_name='测试班', course_id=1, course_name='测试课程'))
    for offset in range(3):
        await add_attendance(db, teacher.id, class_obj.id, date.today() - timedelta(days=offset), 1)
    await db.commit()
    page = await TeachTeacherStatService.get_teacher_records_services(db, teacher.id, 1, 2)
    assert page.total == 3 and len(page.rows) == 2
    assert page.rows[0]['attendanceRate'] == 50.0


async def test_teacher_overview(db, factory):
    teacher = await factory.teacher('孙老师')
    await factory.add(TeachClass(class_name='主讲班', course_id=1, course_name='测试课程', teacher_id=teacher.id))
    await factory.add(TeachClass(class_name='助教班', course_id=1, course_name='测试课程', assistant_id=teacher.id))
    await db.commit()
    overview = await TeachTeacherStatService.get_teacher_overview_services(db, teacher.id)
    roles = sorted(row['teacherRole'] for row in overview['classes'])
    assert roles == ['主讲', '助教'] and overview['stats']['classCount'] == 2
