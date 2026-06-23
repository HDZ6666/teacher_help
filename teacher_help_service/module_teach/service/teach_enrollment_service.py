from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_ast.dao.ast_inventory_dao import AstInventoryDao
from module_ast.service.ast_inventory_service import AstInventoryService
from module_teach.dao.teach_class_dao import TeachClassDao
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.dao.teach_enrollment_dao import TeachEnrollmentDao
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.service.teach_class_service import TeachClassService
from module_teach.entity.do.teach_enrollment_order_do import (
    TeachEnrollmentOrder,
    TeachEnrollmentOrderItem,
    TeachStudentCourseAccount,
)
from module_teach.entity.vo.teach_student_vo import TeachStudentEnrollItemModel, TeachStudentEnrollModel
from exceptions.exception import ServiceException
from utils.common_util import CamelCaseUtil


class TeachEnrollmentService:
    """
    学员报名/续费服务层
    """

    ITEM_TYPE_LABELS = {
        'course': '课程',
        'item': '物品',
        'fee': '费用',
    }
    ORDER_TYPE_LABELS = {
        'enroll': '报名',
        'renew': '续费',
    }
    ORDER_STATUS_LABELS = {
        'pending': '待支付',
        'paid': '已支付',
        'cancelled': '已取消',
    }
    CHARGE_UNITS = {
        'class': '课时',
        'lesson': '课时',
        'month': '月',
        'day': '天',
        'item': '件',
        'fee': '笔',
    }

    @classmethod
    def to_decimal(cls, value, default=0):
        if value in [None, '']:
            return Decimal(str(default))
        return Decimal(str(value)).quantize(Decimal('0.01'))

    @classmethod
    def to_int(cls, value, default=0):
        if value in [None, '']:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def make_order_no(cls):
        return f'EN{datetime.now().strftime("%Y%m%d%H%M%S%f")}'

    @classmethod
    def calc_amount(cls, item: TeachStudentEnrollItemModel):
        quantity = max(cls.to_int(item.quantity, 1), 1)
        unit_price = cls.to_decimal(item.unit_price, 0)
        total_price = (unit_price * quantity).quantize(Decimal('0.01'))
        discount_value = cls.to_decimal(item.discount_value, 0)

        if item.discount_type == 'discount' and discount_value > 0:
            if discount_value <= 10:
                subtotal_price = total_price * discount_value / Decimal('10')
            elif discount_value <= 100:
                subtotal_price = total_price * discount_value / Decimal('100')
            else:
                subtotal_price = total_price
        else:
            subtotal_price = total_price - discount_value

        if subtotal_price < 0:
            subtotal_price = Decimal('0')
        return quantity, total_price, subtotal_price.quantize(Decimal('0.01'))

    @classmethod
    async def normalize_course_item(cls, query_db: AsyncSession, item: TeachStudentEnrollItemModel):
        course = await TeachCourseDao.get_teach_course_by_id(query_db, item.item_id)
        if not course or course.status != 1:
            raise ServiceException(message=f'课程({item.item_name})不存在或已停用')

        price = None
        if item.spec_id:
            prices = await TeachCourseDao.get_prices_by_course_id(query_db, item.item_id)
            price = next((price_item for price_item in prices if price_item.id == item.spec_id), None)
            if not price:
                raise ServiceException(message=f'课程({course.course_name})定价标准不存在')

        charge_type = price.charge_type if price else item.charge_type
        quantity = item.quantity or (price.quantity if price else 1)
        unit_price = price.unit_price if price else item.unit_price
        unit = item.unit or cls.CHARGE_UNITS.get(charge_type, '课时')
        class_name = item.class_name
        if item.class_id:
            class_obj = await TeachClassDao.get_teach_class_by_id(query_db, item.class_id)
            if not class_obj:
                raise ServiceException(message=f'课程({course.course_name})选择的班级不存在')
            if class_obj.status != 1 or class_obj.enroll_status == 3:
                raise ServiceException(message=f'班级({class_obj.class_name})不可招生')
            if class_obj.course_id != course.id:
                raise ServiceException(message=f'班级({class_obj.class_name})与课程({course.course_name})不匹配')
            if (
                class_obj.max_students
                and class_obj.allow_over_capacity != 1
                and (class_obj.current_students or 0) >= class_obj.max_students
            ):
                raise ServiceException(message=f'班级({class_obj.class_name})已满员')
            class_name = class_obj.class_name
        normalized = item.model_copy(
            update={
                'item_name': course.course_name,
                'spec_name': price.price_name if price else item.spec_name,
                'charge_type': charge_type,
                'unit': unit,
                'quantity': quantity,
                'unit_price': unit_price,
                'class_name': class_name,
            }
        )
        return normalized

    @classmethod
    async def normalize_inventory_item(cls, query_db: AsyncSession, item: TeachStudentEnrollItemModel):
        if not item.spec_id:
            raise ServiceException(message=f'物品({item.item_name})请选择规格')
        sku_item = await AstInventoryDao.get_sku_with_item_by_id(query_db, item.spec_id)
        if not sku_item:
            raise ServiceException(message=f'物品({item.item_name})规格不存在')
        sku, ast_item = sku_item
        if ast_item.id != item.item_id:
            raise ServiceException(message=f'物品({item.item_name})规格不匹配')
        if ast_item.status != 1 or sku.status != 1:
            raise ServiceException(message=f'物品({ast_item.item_name})已停用')
        quantity = max(cls.to_int(item.quantity, 1), 1)
        if (sku.stock or 0) < quantity:
            raise ServiceException(message=f'物品({ast_item.item_name}-{sku.sku_name})库存不足')
        return item.model_copy(
            update={
                'item_name': ast_item.item_name,
                'spec_name': sku.sku_name,
                'charge_type': 'item',
                'unit': item.unit or '件',
                'unit_price': sku.price or Decimal('0'),
                'quantity': quantity,
            }
        )

    @classmethod
    async def normalize_fee_item(cls, query_db: AsyncSession, item: TeachStudentEnrollItemModel):
        fee = await AstInventoryDao.get_fee_by_id(query_db, item.item_id)
        if not fee or fee.status != 1:
            raise ServiceException(message=f'费用({item.item_name})不存在或已停用')
        return item.model_copy(
            update={
                'item_name': fee.fee_name,
                'charge_type': 'fee',
                'unit': item.unit or '笔',
                'unit_price': fee.amount or Decimal('0'),
            }
        )

    @classmethod
    async def normalize_enroll_items(cls, query_db: AsyncSession, items: list[TeachStudentEnrollItemModel]):
        result = []
        for index, item in enumerate(items):
            if item.item_type == 'course':
                normalized = await cls.normalize_course_item(query_db, item)
            elif item.item_type == 'item':
                normalized = await cls.normalize_inventory_item(query_db, item)
            else:
                normalized = await cls.normalize_fee_item(query_db, item)

            quantity, total_price, subtotal_price = cls.calc_amount(normalized)
            result.append(
                normalized.model_copy(
                    update={
                        'quantity': quantity,
                        'total_price': total_price,
                        'subtotal_price': subtotal_price,
                        'sort': index,
                    }
                )
            )
        return result

    @classmethod
    async def add_order_item(
        cls,
        query_db: AsyncSession,
        order: TeachEnrollmentOrder,
        item: TeachStudentEnrollItemModel,
        current_user_name: str,
    ):
        order_item = TeachEnrollmentOrderItem(
            order_id=order.id,
            student_id=order.student_id,
            item_type=item.item_type,
            item_id=item.item_id,
            item_name=item.item_name,
            spec_id=item.spec_id,
            spec_name=item.spec_name,
            charge_type=item.charge_type,
            unit=item.unit,
            quantity=item.quantity,
            gift_quantity=item.gift_quantity,
            leave_exempt_count=item.leave_exempt_count,
            unit_price=item.unit_price,
            total_price=item.total_price,
            discount_type=item.discount_type,
            discount_value=item.discount_value,
            subtotal_price=item.subtotal_price,
            start_date=item.start_date,
            end_date=item.end_date,
            validity_type=item.validity_type,
            class_id=item.class_id,
            class_name=item.class_name,
            package_id=item.package_id,
            package_name=item.package_name,
            remark=item.remark,
            sort=item.sort,
            create_by=current_user_name,
            create_time=datetime.now(),
            update_by=current_user_name,
            update_time=datetime.now(),
        )
        return await TeachEnrollmentDao.add_enrollment_order_item(query_db, order_item)

    @classmethod
    async def create_course_account(
        cls,
        query_db: AsyncSession,
        order: TeachEnrollmentOrder,
        order_item: TeachEnrollmentOrderItem,
        item: TeachStudentEnrollItemModel,
        current_user_name: str,
    ):
        total_quantity = (item.quantity or 0) + (item.gift_quantity or 0)
        account = TeachStudentCourseAccount(
            student_id=order.student_id,
            course_id=item.item_id,
            course_name=item.item_name,
            order_id=order.id,
            order_item_id=order_item.id,
            charge_type=item.charge_type,
            unit=item.unit,
            purchased_quantity=item.quantity,
            gift_quantity=item.gift_quantity,
            remaining_quantity=total_quantity,
            leave_exempt_count=item.leave_exempt_count,
            valid_start_date=item.start_date,
            valid_end_date=item.end_date,
            validity_type=item.validity_type,
            class_id=item.class_id,
            class_name=item.class_name,
            remark=item.remark,
            create_by=current_user_name,
            create_time=datetime.now(),
            update_by=current_user_name,
            update_time=datetime.now(),
        )
        return await TeachEnrollmentDao.add_student_course_account(query_db, account)

    @classmethod
    async def create_inventory_sale_record(
        cls,
        query_db: AsyncSession,
        order: TeachEnrollmentOrder,
        item: TeachStudentEnrollItemModel,
        student_name: str,
        current_user_name: str,
    ):
        await AstInventoryService.apply_stock_change(
            query_db,
            sku_id=item.spec_id,
            quantity=-item.quantity,
            business_type='sale',
            source_type='enrollment_order',
            source_id=order.id,
            related_type='student',
            related_name=student_name,
            operator_name=current_user_name,
            record_date=order.enroll_date or date.today(),
            create_by=current_user_name,
            remark=item.remark or f'报名订单{order.order_no}销售出库',
        )

    @classmethod
    async def submit_student_enroll_services(
        cls, query_db: AsyncSession, page_object: TeachStudentEnrollModel, current_user_name: str
    ):
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, page_object.student_id)
        if not student_result:
            raise ServiceException(message='学员不存在')
        student, _, base_user = student_result
        normalized_items = await cls.normalize_enroll_items(query_db, page_object.items)
        total_amount = sum((item.total_price or Decimal('0') for item in normalized_items), Decimal('0'))
        receivable_amount = sum((item.subtotal_price or Decimal('0') for item in normalized_items), Decimal('0'))
        discount_amount = total_amount - receivable_amount
        if discount_amount < 0:
            discount_amount = Decimal('0')

        try:
            order = TeachEnrollmentOrder(
                order_no=cls.make_order_no(),
                student_id=student.id,
                student_name=student.student_name,
                parent_phone=base_user.phone if base_user else None,
                order_type=page_object.order_type or 'enroll',
                order_source='机构创建',
                enroll_date=page_object.enroll_date or date.today(),
                item_count=len(normalized_items),
                total_amount=total_amount.quantize(Decimal('0.01')),
                discount_amount=discount_amount.quantize(Decimal('0.01')),
                receivable_amount=receivable_amount.quantize(Decimal('0.01')),
                paid_amount=receivable_amount.quantize(Decimal('0.01')),
                status='paid',
                performance_owner=page_object.performance_owner,
                performance_type=page_object.performance_type,
                performance_amount=page_object.performance_amount or Decimal('0'),
                remark=page_object.remark,
                create_by=current_user_name,
                create_time=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now(),
            )
            order = await TeachEnrollmentDao.add_enrollment_order(query_db, order)

            for item in normalized_items:
                order_item = await cls.add_order_item(query_db, order, item, current_user_name)
                if item.item_type == 'course':
                    account = await cls.create_course_account(query_db, order, order_item, item, current_user_name)
                    if item.class_id:
                        await TeachClassService.add_student_from_enrollment_services(
                            query_db, item.class_id, order.student_id, account, order_item, current_user_name
                        )
                elif item.item_type == 'item':
                    await cls.create_inventory_sale_record(
                        query_db, order, item, student.student_name, current_user_name
                    )

            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='报名成功',
                result={'id': order.id, 'orderNo': order.order_no, 'receivableAmount': order.receivable_amount},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    def format_course_account_row(cls, account, order_no: str | None = None):
        row = CamelCaseUtil.transform_result(account)
        row['orderNo'] = order_no
        row['chargeTypeName'] = cls.CHARGE_UNITS.get(row.get('chargeType'), row.get('chargeType'))
        row['statusName'] = '有效' if row.get('status') == 'active' else row.get('status')
        return row

    @classmethod
    async def get_student_course_accounts_services(cls, query_db: AsyncSession, student_id: int):
        rows = await TeachEnrollmentDao.get_student_course_accounts(query_db, student_id)
        return [cls.format_course_account_row(account, order_no) for account, order_no in rows]

    @classmethod
    def format_order_item_row(cls, item: TeachEnrollmentOrderItem):
        row = CamelCaseUtil.transform_result(item)
        row['itemTypeName'] = cls.ITEM_TYPE_LABELS.get(row.get('itemType'), row.get('itemType'))
        return row

    @classmethod
    def format_order_row(cls, order: TeachEnrollmentOrder, items: list[TeachEnrollmentOrderItem]):
        row = CamelCaseUtil.transform_result(order)
        item_rows = [cls.format_order_item_row(item) for item in items]
        row['orderTypeName'] = cls.ORDER_TYPE_LABELS.get(row.get('orderType'), row.get('orderType'))
        row['statusName'] = cls.ORDER_STATUS_LABELS.get(row.get('status'), row.get('status'))
        row['items'] = item_rows
        row['itemSummary'] = '、'.join(
            [
                f"{item.get('itemName')}({item.get('specName')})" if item.get('specName') else item.get('itemName')
                for item in item_rows
                if item.get('itemName')
            ]
        )
        return row

    @classmethod
    async def get_student_orders_services(cls, query_db: AsyncSession, student_id: int):
        orders = await TeachEnrollmentDao.get_student_orders(query_db, student_id)
        order_ids = [order.id for order in orders]
        order_items = await TeachEnrollmentDao.get_order_items_by_order_ids(query_db, order_ids)
        item_map = defaultdict(list)
        for item in order_items:
            item_map[item.order_id].append(item)
        return [cls.format_order_row(order, item_map.get(order.id, [])) for order in orders]
