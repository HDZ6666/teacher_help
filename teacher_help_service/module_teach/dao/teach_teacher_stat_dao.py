from datetime import date

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_teach.entity.do.teach_class_do import TeachClass, TeachClassAttendance, TeachClassTeacher
from utils.page_util import PageUtil


class TeachTeacherStatDao:
    """
    老师课时统计数据库操作层（基于班级点名记录 teach_class_attendance）
    """

    @classmethod
    async def sum_attendance_by_teachers(
        cls, db: AsyncSession, teacher_ids: list[int], begin_date: date | None = None, end_date: date | None = None
    ):
        """
        按老师汇总已点名课次数与课时数

        :return: {teacher_id: (课次数, 课时数)}
        """
        if not teacher_ids:
            return {}
        query = select(
            TeachClassAttendance.teacher_id,
            func.count(TeachClassAttendance.id),
            func.coalesce(func.sum(TeachClassAttendance.lesson_hours), 0),
        ).where(TeachClassAttendance.teacher_id.in_(teacher_ids), TeachClassAttendance.del_flag == 0)
        if begin_date:
            query = query.where(TeachClassAttendance.class_date >= begin_date)
        if end_date:
            query = query.where(TeachClassAttendance.class_date <= end_date)
        result = await db.execute(query.group_by(TeachClassAttendance.teacher_id))
        return {row[0]: (row[1] or 0, row[2] or 0) for row in result.all()}

    @classmethod
    def teacher_class_condition(cls, teacher_id: int):
        relation = select(TeachClassTeacher.class_id).where(
            TeachClassTeacher.teacher_id == teacher_id, TeachClassTeacher.del_flag == 0
        )
        return or_(
            TeachClass.teacher_id == teacher_id,
            TeachClass.assistant_id == teacher_id,
            TeachClass.id.in_(relation),
        )

    @classmethod
    async def count_classes_by_teachers(cls, db: AsyncSession, teacher_ids: list[int]):
        """
        按老师统计授课班级数（主讲/助教/班级老师关系任一命中）
        """
        counts = {}
        for teacher_id in teacher_ids:
            result = await db.execute(
                select(func.count(TeachClass.id)).where(
                    TeachClass.del_flag == 0, cls.teacher_class_condition(teacher_id)
                )
            )
            counts[teacher_id] = result.scalar() or 0
        return counts

    @classmethod
    async def get_teacher_classes(cls, db: AsyncSession, teacher_id: int):
        result = await db.execute(
            select(TeachClass)
            .where(TeachClass.del_flag == 0, cls.teacher_class_condition(teacher_id))
            .order_by(desc(TeachClass.id))
        )
        return result.scalars().all()

    @classmethod
    async def get_teacher_attendance_page(
        cls,
        db: AsyncSession,
        teacher_id: int,
        page_num: int,
        page_size: int,
        begin_date: date | None = None,
        end_date: date | None = None,
    ):
        query = select(TeachClassAttendance).where(
            TeachClassAttendance.teacher_id == teacher_id, TeachClassAttendance.del_flag == 0
        )
        if begin_date:
            query = query.where(TeachClassAttendance.class_date >= begin_date)
        if end_date:
            query = query.where(TeachClassAttendance.class_date <= end_date)
        query = query.order_by(desc(TeachClassAttendance.class_date), desc(TeachClassAttendance.id))
        return await PageUtil.paginate(db, query, page_num, page_size, True)
