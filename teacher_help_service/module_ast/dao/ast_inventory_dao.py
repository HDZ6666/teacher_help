from sqlalchemy import case, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_ast.entity.do.ast_fee_course_do import AstFeeCourse
from module_ast.entity.do.ast_fee_item_do import AstFeeItem
from module_ast.entity.do.ast_item_course_do import AstItemCourse
from module_ast.entity.do.ast_item_do import AstItem
from module_ast.entity.do.ast_item_sku_do import AstItemSku
from module_ast.entity.do.ast_item_stock_record_do import AstItemStockRecord
from module_ast.entity.do.ast_purchase_order_do import AstPurchaseOrder
from module_ast.entity.do.ast_purchase_order_item_do import AstPurchaseOrderItem
from module_ast.entity.vo.ast_inventory_vo import AstFeeItemPageQueryModel, AstStockRecordPageQueryModel
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from utils.page_util import PageUtil


class AstInventoryDao:
    """
    物品费用管理模块数据库操作层
    """

    @classmethod
    async def get_item_skus_by_item_ids(cls, db: AsyncSession, item_ids: list[int]):
        if not item_ids:
            return []
        result = await db.execute(
            select(AstItemSku)
            .where(AstItemSku.item_id.in_(item_ids), AstItemSku.del_flag == 0)
            .order_by(AstItemSku.item_id, AstItemSku.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_item_skus_by_item_id(cls, db: AsyncSession, item_id: int):
        result = await db.execute(
            select(AstItemSku)
            .where(AstItemSku.item_id == item_id, AstItemSku.del_flag == 0)
            .order_by(AstItemSku.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_sku_with_item_by_id(cls, db: AsyncSession, sku_id: int):
        result = await db.execute(
            select(AstItemSku, AstItem)
            .join(AstItem, AstItemSku.item_id == AstItem.id)
            .where(AstItemSku.id == sku_id, AstItemSku.del_flag == 0, AstItem.del_flag == 0)
        )
        return result.first()

    @classmethod
    async def add_item_sku_dao(cls, db: AsyncSession, sku: AstItemSku):
        db.add(sku)
        await db.flush()
        await db.refresh(sku)
        return sku

    @classmethod
    async def get_item_courses_by_item_ids(cls, db: AsyncSession, item_ids: list[int]):
        if not item_ids:
            return []
        result = await db.execute(
            select(AstItemCourse).where(AstItemCourse.item_id.in_(item_ids)).order_by(AstItemCourse.id)
        )
        return result.scalars().all()

    @classmethod
    async def delete_item_courses_by_item_id(cls, db: AsyncSession, item_id: int):
        await db.execute(delete(AstItemCourse).where(AstItemCourse.item_id == item_id))

    @classmethod
    async def add_item_course_dao(cls, db: AsyncSession, item_course: AstItemCourse):
        db.add(item_course)
        await db.flush()
        await db.refresh(item_course)
        return item_course

    @classmethod
    async def update_item_sku_dao(cls, db: AsyncSession, sku_id: int, values: dict):
        await db.execute(update(AstItemSku).where(AstItemSku.id == sku_id).values(**values))

    @classmethod
    async def soft_delete_item_sku_dao(cls, db: AsyncSession, sku_id: int, update_by: str = ''):
        await db.execute(
            update(AstItemSku)
            .where(AstItemSku.id == sku_id)
            .values(del_flag=1, status=0, update_by=update_by)
        )

    @classmethod
    async def soft_delete_item_skus_by_item_id(cls, db: AsyncSession, item_id: int, update_by: str = ''):
        await db.execute(
            update(AstItemSku)
            .where(AstItemSku.item_id == item_id)
            .values(del_flag=1, status=0, update_by=update_by)
        )

    @classmethod
    async def refresh_item_stock_dao(cls, db: AsyncSession, item_id: int):
        total_stock, available_stock = (
            await db.execute(
                select(
                    func.coalesce(func.sum(AstItemSku.stock), 0),
                    func.coalesce(func.sum(AstItemSku.available_stock), 0),
                ).where(AstItemSku.item_id == item_id, AstItemSku.del_flag == 0)
            )
        ).first()
        await db.execute(
            update(AstItem)
            .where(AstItem.id == item_id)
            .values(total_stock=int(total_stock or 0), available_stock=int(available_stock or 0))
        )

    @classmethod
    async def get_available_item_list(cls, db: AsyncSession, keyword: str | None = None):
        query = select(AstItem).where(AstItem.del_flag == 0, AstItem.status == 1)
        if keyword:
            query = query.where(AstItem.item_name.like(f'%{keyword}%'))
        result = await db.execute(query.order_by(desc(AstItem.create_time)))
        return result.scalars().all()

    @classmethod
    async def get_student_role_options(cls, db: AsyncSession, keyword: str | None = None):
        query = select(TeachStudent).where(TeachStudent.del_flag == '0')
        if keyword:
            query = query.where(TeachStudent.student_name.like(f'%{keyword}%'))
        result = await db.execute(query.order_by(desc(TeachStudent.create_time)).limit(50))
        return result.scalars().all()

    @classmethod
    async def get_teacher_role_options(cls, db: AsyncSession, keyword: str | None = None):
        query = select(TeachTeacher).where(TeachTeacher.del_flag == '0', TeachTeacher.status == '0')
        if keyword:
            query = query.where(TeachTeacher.teacher_name.like(f'%{keyword}%'))
        result = await db.execute(query.order_by(desc(TeachTeacher.create_time)).limit(50))
        return result.scalars().all()

    @classmethod
    async def get_stock_record_list(
        cls, db: AsyncSession, query_object: AstStockRecordPageQueryModel, is_page: bool = False
    ):
        query = cls.build_stock_record_query(query_object).order_by(
            desc(AstItemStockRecord.create_time), desc(AstItemStockRecord.id)
        )
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    def build_stock_record_query(cls, query_object: AstStockRecordPageQueryModel):
        keyword = query_object.keyword or query_object.item_name
        conditions = []
        if query_object.exclude_voided is not False:
            conditions.append(AstItemStockRecord.del_flag == 0)
        if keyword:
            conditions.append(AstItemStockRecord.item_name.like(f'%{keyword}%'))
        if query_object.item_names:
            item_names = [item.strip() for item in query_object.item_names.split(',') if item.strip()]
            if item_names:
                conditions.append(or_(*[AstItemStockRecord.item_name.like(f'%{item_name}%') for item_name in item_names]))
        if query_object.business_type:
            conditions.append(AstItemStockRecord.business_type == query_object.business_type)
        if query_object.stock_type == 'in':
            conditions.append(AstItemStockRecord.quantity > 0)
        elif query_object.stock_type == 'out':
            conditions.append(AstItemStockRecord.quantity < 0)
        if query_object.related_type:
            role_type_map = {
                'student': ['student', 'learner'],
                'staff': ['staff', 'teacher', 'employee'],
                'other': ['other', 'admin'],
            }
            related_types = role_type_map.get(query_object.related_type, [query_object.related_type])
            conditions.append(AstItemStockRecord.related_type.in_(related_types))
        if query_object.related_name:
            conditions.append(AstItemStockRecord.related_name.like(f'%{query_object.related_name}%'))
        if query_object.begin_time:
            conditions.append(AstItemStockRecord.record_date >= str(query_object.begin_time)[:10])
        if query_object.end_time:
            conditions.append(AstItemStockRecord.record_date <= str(query_object.end_time)[:10])
        return select(AstItemStockRecord).where(*conditions)

    @classmethod
    async def get_stock_record_summary(cls, db: AsyncSession, query_object: AstStockRecordPageQueryModel):
        query = cls.build_stock_record_query(query_object).subquery()
        result = await db.execute(
            select(
                func.count(query.c.id),
                func.coalesce(func.sum(case((query.c.quantity > 0, query.c.quantity), else_=0)), 0),
                func.coalesce(func.sum(case((query.c.quantity < 0, func.abs(query.c.quantity)), else_=0)), 0),
                func.coalesce(func.sum(query.c.quantity), 0),
            )
        )
        return result.first()

    @classmethod
    async def get_stock_record_by_id(cls, db: AsyncSession, record_id: int):
        result = await db.execute(select(AstItemStockRecord).where(AstItemStockRecord.id == record_id))
        return result.scalars().first()

    @classmethod
    async def add_stock_record_dao(cls, db: AsyncSession, record: AstItemStockRecord):
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    @classmethod
    async def update_stock_record_dao(cls, db: AsyncSession, record_id: int, values: dict):
        await db.execute(update(AstItemStockRecord).where(AstItemStockRecord.id == record_id).values(**values))

    @classmethod
    async def add_purchase_order_dao(cls, db: AsyncSession, order: AstPurchaseOrder):
        db.add(order)
        await db.flush()
        await db.refresh(order)
        return order

    @classmethod
    async def add_purchase_order_item_dao(cls, db: AsyncSession, order_item: AstPurchaseOrderItem):
        db.add(order_item)
        await db.flush()
        await db.refresh(order_item)
        return order_item

    @classmethod
    async def get_purchase_order_by_id(cls, db: AsyncSession, order_id: int):
        result = await db.execute(
            select(AstPurchaseOrder).where(AstPurchaseOrder.id == order_id, AstPurchaseOrder.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def get_purchase_orders_by_ids(cls, db: AsyncSession, order_ids: list[int]):
        if not order_ids:
            return []
        result = await db.execute(
            select(AstPurchaseOrder).where(AstPurchaseOrder.id.in_(order_ids)).order_by(desc(AstPurchaseOrder.id))
        )
        return result.scalars().all()

    @classmethod
    async def get_purchase_order_items_by_order_id(cls, db: AsyncSession, order_id: int):
        result = await db.execute(
            select(AstPurchaseOrderItem)
            .where(AstPurchaseOrderItem.order_id == order_id, AstPurchaseOrderItem.del_flag == 0)
            .order_by(AstPurchaseOrderItem.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_sku_by_item_name_and_sku_name(cls, db: AsyncSession, item_name: str, sku_name: str | None = None):
        query = (
            select(AstItemSku, AstItem)
            .join(AstItem, AstItemSku.item_id == AstItem.id)
            .where(AstItem.item_name == item_name, AstItemSku.del_flag == 0, AstItem.del_flag == 0)
            .order_by(AstItemSku.id)
        )
        if sku_name:
            query = query.where(AstItemSku.sku_name == sku_name)
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def get_fee_list(cls, db: AsyncSession, query_object: AstFeeItemPageQueryModel, is_page: bool = False):
        query = (
            select(AstFeeItem)
            .where(
                AstFeeItem.del_flag == 0,
                AstFeeItem.fee_name.like(f'%{query_object.fee_name}%') if query_object.fee_name else True,
                AstFeeItem.status == query_object.status if query_object.status is not None else True,
            )
            .order_by(AstFeeItem.sort, desc(AstFeeItem.create_time), desc(AstFeeItem.id))
        )
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_fee_by_id(cls, db: AsyncSession, fee_id: int):
        result = await db.execute(select(AstFeeItem).where(AstFeeItem.id == fee_id, AstFeeItem.del_flag == 0))
        return result.scalars().first()

    @classmethod
    async def add_fee_dao(cls, db: AsyncSession, fee: AstFeeItem):
        db.add(fee)
        await db.flush()
        await db.refresh(fee)
        return fee

    @classmethod
    async def update_fee_dao(cls, db: AsyncSession, fee_id: int, values: dict):
        await db.execute(update(AstFeeItem).where(AstFeeItem.id == fee_id).values(**values))

    @classmethod
    async def delete_fee_dao(cls, db: AsyncSession, fee_id: int, update_by: str = ''):
        await db.execute(
            update(AstFeeItem).where(AstFeeItem.id == fee_id).values(del_flag=1, update_by=update_by)
        )

    @classmethod
    async def get_fee_courses_by_fee_ids(cls, db: AsyncSession, fee_ids: list[int]):
        if not fee_ids:
            return []
        result = await db.execute(
            select(AstFeeCourse).where(AstFeeCourse.fee_id.in_(fee_ids)).order_by(AstFeeCourse.id)
        )
        return result.scalars().all()

    @classmethod
    async def delete_fee_courses_by_fee_id(cls, db: AsyncSession, fee_id: int):
        await db.execute(delete(AstFeeCourse).where(AstFeeCourse.fee_id == fee_id))

    @classmethod
    async def add_fee_course_dao(cls, db: AsyncSession, fee_course: AstFeeCourse):
        db.add(fee_course)
        await db.flush()
        await db.refresh(fee_course)
        return fee_course
