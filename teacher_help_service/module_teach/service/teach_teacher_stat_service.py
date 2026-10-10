from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_teach.dao.teach_teacher_dao import TeachTeacherDao
from module_teach.dao.teach_teacher_stat_dao import TeachTeacherStatDao
from utils.common_util import CamelCaseUtil


class TeachTeacherStatService:
    """
    老师课时统计服务层：上月/本月/累计已上课次与课时、授课班级、上课记录
    课时口径：班级点名记录(teach_class_attendance)的授课课时 lesson_hours，
    按点名记录上的上课老师归属；已撤销的点名不计入
    """

    @classmethod
    def month_range(cls, today: date | None = None):
        today = today or date.today()
        this_month_start = today.replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return (this_month_start, today), (last_month_start, last_month_end)

    @classmethod
    def parse_date(cls, value):
        if not value:
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
        except ValueError:
            raise ServiceException(message='日期格式不正确(应为YYYY-MM-DD)')

    @classmethod
    def to_number(cls, value):
        value = Decimal(str(value or 0))
        return int(value) if value == value.to_integral() else float(value)

    @classmethod
    async def get_teacher_stats_services(
        cls, query_db: AsyncSession, teacher_ids: list[int], today: date | None = None
    ):
        teacher_ids = sorted({int(item) for item in teacher_ids if item})
        if not teacher_ids:
            return []
        if len(teacher_ids) > 200:
            raise ServiceException(message='一次最多统计200位老师')
        (this_start, this_end), (last_start, last_end) = cls.month_range(today)
        this_month = await TeachTeacherStatDao.sum_attendance_by_teachers(query_db, teacher_ids, this_start, this_end)
        last_month = await TeachTeacherStatDao.sum_attendance_by_teachers(query_db, teacher_ids, last_start, last_end)
        total = await TeachTeacherStatDao.sum_attendance_by_teachers(query_db, teacher_ids)
        class_counts = await TeachTeacherStatDao.count_classes_by_teachers(query_db, teacher_ids)
        rows = []
        for teacher_id in teacher_ids:
            rows.append(
                {
                    'teacherId': teacher_id,
                    'classCount': class_counts.get(teacher_id, 0),
                    'thisMonthLessons': this_month.get(teacher_id, (0, 0))[0],
                    'thisMonthHours': cls.to_number(this_month.get(teacher_id, (0, 0))[1]),
                    'lastMonthLessons': last_month.get(teacher_id, (0, 0))[0],
                    'lastMonthHours': cls.to_number(last_month.get(teacher_id, (0, 0))[1]),
                    'totalLessons': total.get(teacher_id, (0, 0))[0],
                    'totalHours': cls.to_number(total.get(teacher_id, (0, 0))[1]),
                }
            )
        return rows

    @classmethod
    async def get_teacher_overview_services(cls, query_db: AsyncSession, teacher_id: int):
        teacher = await TeachTeacherDao.get_teach_teacher_by_id(query_db, teacher_id)
        if not teacher:
            raise ServiceException(message='老师不存在')
        stats = (await cls.get_teacher_stats_services(query_db, [teacher_id]))[0]
        classes = []
        for class_obj in await TeachTeacherStatDao.get_teacher_classes(query_db, teacher_id):
            row = CamelCaseUtil.transform_result(class_obj)
            if class_obj.teacher_id == teacher_id:
                row['teacherRole'] = '主讲'
            elif class_obj.assistant_id == teacher_id:
                row['teacherRole'] = '助教'
            else:
                row['teacherRole'] = '任课'
            classes.append(row)
        return {'stats': stats, 'classes': classes}

    @classmethod
    async def get_teacher_records_services(
        cls,
        query_db: AsyncSession,
        teacher_id: int,
        page_num: int,
        page_size: int,
        begin_date=None,
        end_date=None,
    ):
        page = await TeachTeacherStatDao.get_teacher_attendance_page(
            query_db,
            teacher_id,
            max(int(page_num or 1), 1),
            min(max(int(page_size or 10), 1), 100),
            cls.parse_date(begin_date),
            cls.parse_date(end_date),
        )
        for row in page.rows:
            expected = row.get('studentCount') or 0
            actual = (row.get('presentCount') or 0) + (row.get('lateCount') or 0)
            row['classTime'] = f"{row.get('classDate')} {row.get('startTime')}~{row.get('endTime')}"
            row['expectedCount'] = expected
            row['actualCount'] = actual
            row['attendanceRate'] = round(actual / expected * 100, 2) if expected else 0
        return page
