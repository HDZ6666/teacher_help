from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.entity.do.teach_enrollment_order_do import (
    TeachEnrollmentOrder,
    TeachEnrollmentOrderItem,
    TeachStudentCourseAccount,
)


class TeachEnrollmentDao:
    """
    学员报名/续费数据库操作层
    """

    @classmethod
    async def add_enrollment_order(cls, db: AsyncSession, order: TeachEnrollmentOrder):
        db.add(order)
        await db.flush()
        await db.refresh(order)
        return order

    @classmethod
    async def add_enrollment_order_item(cls, db: AsyncSession, order_item: TeachEnrollmentOrderItem):
        db.add(order_item)
        await db.flush()
        await db.refresh(order_item)
        return order_item

    @classmethod
    async def add_student_course_account(cls, db: AsyncSession, account: TeachStudentCourseAccount):
        db.add(account)
        await db.flush()
        await db.refresh(account)
        return account

    @classmethod
    async def get_student_course_accounts(cls, db: AsyncSession, student_id: int):
        result = await db.execute(
            select(TeachStudentCourseAccount, TeachEnrollmentOrder.order_no)
            .join(TeachEnrollmentOrder, TeachStudentCourseAccount.order_id == TeachEnrollmentOrder.id)
            .where(
                and_(
                    TeachStudentCourseAccount.student_id == student_id,
                    TeachStudentCourseAccount.del_flag == 0,
                    TeachEnrollmentOrder.del_flag == 0,
                )
            )
            .order_by(desc(TeachStudentCourseAccount.create_time), desc(TeachStudentCourseAccount.id))
        )
        return result.all()

    @classmethod
    async def get_student_orders(cls, db: AsyncSession, student_id: int):
        result = await db.execute(
            select(TeachEnrollmentOrder)
            .where(TeachEnrollmentOrder.student_id == student_id, TeachEnrollmentOrder.del_flag == 0)
            .order_by(desc(TeachEnrollmentOrder.create_time), desc(TeachEnrollmentOrder.id))
        )
        return result.scalars().all()

    @classmethod
    async def get_order_items_by_order_ids(cls, db: AsyncSession, order_ids: list[int]):
        if not order_ids:
            return []
        result = await db.execute(
            select(TeachEnrollmentOrderItem)
            .where(TeachEnrollmentOrderItem.order_id.in_(order_ids), TeachEnrollmentOrderItem.del_flag == 0)
            .order_by(TeachEnrollmentOrderItem.order_id, TeachEnrollmentOrderItem.sort, TeachEnrollmentOrderItem.id)
        )
        return result.scalars().all()
