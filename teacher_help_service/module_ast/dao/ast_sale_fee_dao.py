from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_ast.entity.do.ast_fee_item_do import AstFeeItem
from module_ast.entity.do.ast_item_stock_record_do import AstItemStockRecord
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_enrollment_order_do import TeachEnrollmentOrder, TeachEnrollmentOrderItem


class AstSaleFeeDao:
    """
    销售订单详情、费用导入数据库操作层
    """

    @classmethod
    async def get_order(cls, db: AsyncSession, order_id: int):
        result = await db.execute(
            select(TeachEnrollmentOrder).where(TeachEnrollmentOrder.id == order_id, TeachEnrollmentOrder.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def get_order_items(cls, db: AsyncSession, order_id: int):
        result = await db.execute(
            select(TeachEnrollmentOrderItem)
            .where(TeachEnrollmentOrderItem.order_id == order_id, TeachEnrollmentOrderItem.del_flag == 0)
            .order_by(TeachEnrollmentOrderItem.sort, TeachEnrollmentOrderItem.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_order_stock_records(cls, db: AsyncSession, order_id: int):
        """
        订单关联的出入库流水（含已作废）
        """
        result = await db.execute(
            select(AstItemStockRecord)
            .where(AstItemStockRecord.source_type == 'enrollment_order', AstItemStockRecord.source_id == order_id)
            .order_by(AstItemStockRecord.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_fee_names(cls, db: AsyncSession):
        result = await db.execute(select(AstFeeItem.fee_name).where(AstFeeItem.del_flag == 0))
        return {name for name in result.scalars().all() if name}

    @classmethod
    async def get_courses(cls, db: AsyncSession):
        result = await db.execute(select(TeachCourse).where(TeachCourse.del_flag == 0))
        return result.scalars().all()
