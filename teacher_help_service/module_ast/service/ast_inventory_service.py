from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
import io
from itertools import product
from uuid import uuid4
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_ast.dao.ast_inventory_dao import AstInventoryDao
from module_ast.entity.do.ast_fee_course_do import AstFeeCourse
from module_ast.entity.do.ast_fee_item_do import AstFeeItem
from module_ast.entity.do.ast_item_course_do import AstItemCourse
from module_ast.entity.do.ast_item_do import AstItem
from module_ast.entity.do.ast_item_sku_do import AstItemSku
from module_ast.entity.do.ast_item_stock_record_do import AstItemStockRecord
from module_ast.entity.do.ast_purchase_order_do import AstPurchaseOrder
from module_ast.entity.do.ast_purchase_order_item_do import AstPurchaseOrderItem
from module_ast.entity.vo.ast_inventory_vo import (
    AddAstFeeItemModel,
    AddInventoryStockModel,
    AddPurchaseOrderModel,
    AddReceiveStockModel,
    AddReturnStockModel,
    AstFeeItemPageQueryModel,
    AstStockOperationItemModel,
    AstStockRecordPageQueryModel,
    ChangeAstFeeStatusModel,
    DeleteAstFeeItemModel,
    EditAstFeeItemModel,
)
from exceptions.exception import ServiceException
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class AstInventoryService:
    """
    物品费用管理模块服务层
    """

    BUSINESS_TYPE_LABELS = {
        'sale': '销售',
        'purchase': '采购',
        'receive': '领用',
        'return': '退领',
        'inventory': '盘点',
    }
    ROLE_TYPE_LABELS = {
        'student': '学员',
        'learner': '学员',
        'staff': '员工',
        'teacher': '员工',
        'employee': '员工',
        'other': '其他',
        'admin': '其他',
    }
    PAYMENT_METHOD_LABELS = {
        'cash': '现金',
        'wechat': '微信',
        'alipay': '支付宝',
        'bank': '银行卡',
        'pos': 'POS机',
        'transfer': '转账',
    }
    PURCHASE_STATUS_LABELS = {
        0: '草稿',
        1: '已完成',
        2: '已取消',
    }

    @classmethod
    def parse_date(cls, value=None):
        if value is None or value == '':
            return date.today()
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        value_str = str(value).replace('Z', '').replace('/', '-')
        try:
            return datetime.fromisoformat(value_str).date()
        except ValueError:
            return date.fromisoformat(value_str[:10])

    @classmethod
    def to_decimal(cls, value, default=0):
        if value is None or value == '':
            return Decimal(str(default))
        return Decimal(str(value))

    @classmethod
    def to_int(cls, value, default=0):
        if value is None or value == '':
            return default
        return int(value)

    @classmethod
    def make_no(cls, prefix: str):
        return f'{prefix}{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    async def get_role_options_services(cls, query_db: AsyncSession, role_type: str | None, keyword: str | None = None):
        if role_type == 'student':
            students = await AstInventoryDao.get_student_role_options(query_db, keyword)
            return [{'id': student.id, 'label': student.student_name, 'value': student.student_name} for student in students]
        if role_type in ['staff', 'teacher', 'employee']:
            teachers = await AstInventoryDao.get_teacher_role_options(query_db, keyword)
            return [{'id': teacher.id, 'label': teacher.teacher_name, 'value': teacher.teacher_name} for teacher in teachers]
        return []

    @classmethod
    def split_values(cls, value):
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [item.strip() for item in str(value).replace('，', ',').split(',') if item.strip()]

    @classmethod
    def normalize_item_save_payload(cls, page_object):
        """
        兼容前端规格结构，补齐后端 item 字段。
        """
        if getattr(page_object, 'single_price', None) is not None and page_object.default_price is None:
            page_object.default_price = page_object.single_price

        specs = getattr(page_object, 'specs', None) or []
        valid_specs = [item for item in specs if item.get('name') and item.get('tags')]
        if valid_specs:
            first_spec = valid_specs[0]
            page_object.spec1_name = page_object.spec1_name or first_spec.get('name')
            page_object.spec1_values = page_object.spec1_values or ','.join(first_spec.get('tags') or [])
        if len(valid_specs) > 1:
            second_spec = valid_specs[1]
            page_object.spec2_name = page_object.spec2_name or second_spec.get('name')
            page_object.spec2_values = page_object.spec2_values or ','.join(second_spec.get('tags') or [])

        item_images = getattr(page_object, 'item_images', None) or []
        if item_images and not page_object.image_url:
            first_image = item_images[0]
            if isinstance(first_image, dict):
                page_object.image_url = first_image.get('url') or first_image.get('response', {}).get('url')
            elif isinstance(first_image, str):
                page_object.image_url = first_image

    @classmethod
    def build_sku_payloads(cls, page_object):
        default_price = cls.to_decimal(getattr(page_object, 'default_price', None), 0)
        raw_skus = getattr(page_object, 'skus', None) or []
        desired_skus = []

        for index, raw_sku in enumerate(raw_skus):
            spec_list = raw_sku.get('specs') or []
            spec1_value = raw_sku.get('spec1Value') or raw_sku.get('spec1_value')
            spec2_value = raw_sku.get('spec2Value') or raw_sku.get('spec2_value')
            if spec_list:
                spec1_value = spec1_value or spec_list[0].get('value')
                if len(spec_list) > 1:
                    spec2_value = spec2_value or spec_list[1].get('value')
            sku_name = raw_sku.get('skuName') or raw_sku.get('sku_name') or raw_sku.get('specText') or raw_sku.get('spec_text')
            if not sku_name:
                sku_name = ', '.join([item for item in [spec1_value, spec2_value] if item]) or '默认'
            desired_skus.append(
                {
                    'id': raw_sku.get('id') if isinstance(raw_sku.get('id'), int) else None,
                    'sku_no': raw_sku.get('skuNo') or raw_sku.get('sku_no'),
                    'sku_name': sku_name,
                    'spec1_value': spec1_value,
                    'spec2_value': spec2_value,
                    'price': cls.to_decimal(raw_sku.get('price'), default_price),
                    'cost_price': cls.to_decimal(raw_sku.get('costPrice') or raw_sku.get('cost_price'), 0),
                    'stock': cls.to_int(raw_sku.get('stock'), 0),
                    'status': cls.to_int(raw_sku.get('status'), 1),
                    'sort': index,
                }
            )

        if desired_skus:
            return desired_skus

        spec1_values = cls.split_values(getattr(page_object, 'spec1_values', None))
        spec2_values = cls.split_values(getattr(page_object, 'spec2_values', None))
        if spec1_values and spec2_values:
            combos = product(spec1_values, spec2_values)
        elif spec1_values:
            combos = [(value, None) for value in spec1_values]
        else:
            combos = [(None, None)]

        for index, (spec1_value, spec2_value) in enumerate(combos):
            sku_name = ', '.join([item for item in [spec1_value, spec2_value] if item]) or '默认'
            desired_skus.append(
                {
                    'sku_no': None,
                    'sku_name': sku_name,
                    'spec1_value': spec1_value,
                    'spec2_value': spec2_value,
                    'price': default_price,
                    'cost_price': Decimal('0'),
                    'stock': 0,
                    'status': 1,
                    'sort': index,
                }
            )
        return desired_skus

    @classmethod
    def get_sku_key(cls, sku):
        if isinstance(sku, dict):
            return f"{sku.get('spec1_value') or ''}|{sku.get('spec2_value') or ''}|{sku.get('sku_name') or ''}"
        return f'{sku.spec1_value or ""}|{sku.spec2_value or ""}|{sku.sku_name or ""}'

    @classmethod
    async def sync_item_skus_services(cls, query_db: AsyncSession, item: AstItem, page_object, current_user_name: str):
        desired_skus = cls.build_sku_payloads(page_object)
        old_skus = await AstInventoryDao.get_item_skus_by_item_id(query_db, item.id)
        old_sku_map = {cls.get_sku_key(sku): sku for sku in old_skus}
        used_sku_ids = set()

        for desired in desired_skus:
            old_sku = old_sku_map.get(cls.get_sku_key(desired))
            if old_sku:
                used_sku_ids.add(old_sku.id)
                await AstInventoryDao.update_item_sku_dao(
                    query_db,
                    old_sku.id,
                    {
                        'sku_name': desired['sku_name'],
                        'spec1_value': desired['spec1_value'],
                        'spec2_value': desired['spec2_value'],
                        'price': desired['price'],
                        'cost_price': desired['cost_price'] if old_sku.cost_price in [None, 0] else old_sku.cost_price,
                        'status': desired['status'],
                        'update_by': current_user_name,
                        'update_time': datetime.now(),
                    },
                )
                continue

            new_sku = AstItemSku(
                item_id=item.id,
                sku_no=desired['sku_no'] or cls.make_no('SKU'),
                sku_name=desired['sku_name'],
                spec1_value=desired['spec1_value'],
                spec2_value=desired['spec2_value'],
                price=desired['price'],
                cost_price=desired['cost_price'],
                stock=desired['stock'],
                available_stock=desired['stock'],
                status=desired['status'],
                create_by=current_user_name,
                create_time=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now(),
            )
            new_sku = await AstInventoryDao.add_item_sku_dao(query_db, new_sku)
            used_sku_ids.add(new_sku.id)

        for old_sku in old_skus:
            if old_sku.id in used_sku_ids:
                continue
            if (old_sku.stock or 0) == 0 and (old_sku.available_stock or 0) == 0:
                await AstInventoryDao.soft_delete_item_sku_dao(query_db, old_sku.id, current_user_name)
            else:
                await AstInventoryDao.update_item_sku_dao(
                    query_db,
                    old_sku.id,
                    {'status': 0, 'update_by': current_user_name, 'update_time': datetime.now()},
                )

        await AstInventoryDao.refresh_item_stock_dao(query_db, item.id)

    @classmethod
    def format_price_range(cls, skus):
        prices = [cls.to_decimal(sku.price, 0) for sku in skus]
        if not prices:
            return '¥ 0.00'
        min_price = min(prices)
        max_price = max(prices)
        if min_price == max_price:
            return f'¥ {min_price:.2f}'
        return f'¥ {min_price:.2f} - ¥ {max_price:.2f}'

    @classmethod
    def format_sku(cls, sku: AstItemSku):
        spec_text = sku.sku_name or ', '.join([item for item in [sku.spec1_value, sku.spec2_value] if item]) or '默认'
        return {
            'id': sku.id,
            'itemId': sku.item_id,
            'skuNo': sku.sku_no,
            'skuName': sku.sku_name,
            'specText': spec_text,
            'spec1Value': sku.spec1_value,
            'spec2Value': sku.spec2_value,
            'price': sku.price or Decimal('0'),
            'costPrice': sku.cost_price or Decimal('0'),
            'stock': sku.stock or 0,
            'availableStock': sku.available_stock or 0,
            'status': sku.status,
            'remark': sku.remark,
        }

    @classmethod
    def format_item_row(cls, item_row: dict, skus: list[AstItemSku], courses=None):
        warning_stock = cls.to_int(item_row.get('warningStock'), 0)
        total_stock = cls.to_int(item_row.get('totalStock'), 0)
        item_row['itemCode'] = item_row.get('itemNo')
        item_row['skuCount'] = len(skus)
        item_row['priceRange'] = cls.format_price_range(skus)
        item_row['enableStock'] = item_row.get('enableStock') if item_row.get('enableStock') is not None else 1
        item_row['warningStock'] = warning_stock
        item_row['isWarning'] = warning_stock > 0 and total_stock <= warning_stock
        item_row['onlineSale'] = item_row.get('onlineSale') if item_row.get('onlineSale') is not None else 0
        item_row['singlePrice'] = item_row.get('defaultPrice')
        item_row['skus'] = [cls.format_sku(sku) for sku in skus]
        item_row['itemImages'] = [item_row.get('imageUrl')] if item_row.get('imageUrl') else []
        item_row['specs'] = cls.build_front_specs(item_row)
        cls.build_item_course_row(item_row, courses or [])
        return item_row

    @classmethod
    def build_item_course_row(cls, item_row: dict, courses):
        course_ids = [course.course_id for course in courses]
        course_names = [course.course_name for course in courses if course.course_name]
        item_row['courseIds'] = course_ids
        item_row['courseNames'] = course_names
        item_row['courseName'] = '、'.join(course_names)
        item_row['courses'] = [CamelCaseUtil.transform_result(course) for course in courses]
        return item_row

    @classmethod
    async def attach_item_courses(cls, query_db: AsyncSession, item_rows):
        item_ids = [row.get('id') for row in item_rows if row.get('id')]
        courses = await AstInventoryDao.get_item_courses_by_item_ids(query_db, item_ids)
        course_map = defaultdict(list)
        for course in courses:
            course_map[course.item_id].append(course)
        return [cls.build_item_course_row(row, course_map.get(row.get('id'), [])) for row in item_rows]

    @classmethod
    def build_item_courses(cls, item_id: int, page_object, current_user_name: str):
        result = []
        if getattr(page_object, 'courses', None):
            for course in page_object.courses:
                if isinstance(course, dict):
                    course_id = course.get('courseId') or course.get('course_id') or course.get('id')
                    course_name = course.get('courseName') or course.get('course_name')
                else:
                    course_id = getattr(course, 'course_id', None) or getattr(course, 'id', None)
                    course_name = getattr(course, 'course_name', None)
                if course_id:
                    result.append({'course_id': course_id, 'course_name': course_name})
        else:
            course_ids = getattr(page_object, 'course_ids', None) or []
            course_names = getattr(page_object, 'course_names', None) or []
            for index, course_id in enumerate(course_ids):
                result.append(
                    {
                        'course_id': course_id,
                        'course_name': course_names[index] if index < len(course_names) else None,
                    }
                )

        seen = set()
        courses = []
        for course in result:
            if course['course_id'] in seen:
                continue
            seen.add(course['course_id'])
            courses.append(
                AstItemCourse(
                    item_id=item_id,
                    course_id=course['course_id'],
                    course_name=course['course_name'],
                    create_by=current_user_name,
                    create_time=datetime.now(),
                )
            )
        return courses

    @classmethod
    async def save_item_courses(cls, query_db: AsyncSession, item_id: int, page_object, current_user_name: str):
        await AstInventoryDao.delete_item_courses_by_item_id(query_db, item_id)
        for item_course in cls.build_item_courses(item_id, page_object, current_user_name):
            await AstInventoryDao.add_item_course_dao(query_db, item_course)

    @classmethod
    def build_front_specs(cls, item_row: dict):
        specs = []
        if item_row.get('spec1Name'):
            specs.append(
                {
                    'name': item_row.get('spec1Name'),
                    'tags': cls.split_values(item_row.get('spec1Values')),
                    'inputVisible': False,
                    'inputValue': '',
                }
            )
        if item_row.get('spec2Name'):
            specs.append(
                {
                    'name': item_row.get('spec2Name'),
                    'tags': cls.split_values(item_row.get('spec2Values')),
                    'inputVisible': False,
                    'inputValue': '',
                }
            )
        if not specs:
            specs.append({'name': '', 'tags': [], 'inputVisible': False, 'inputValue': ''})
        return specs

    @classmethod
    async def get_item_skus_services(cls, query_db: AsyncSession, item_id: int):
        skus = await AstInventoryDao.get_item_skus_by_item_id(query_db, item_id)
        return [cls.format_sku(sku) for sku in skus]

    @classmethod
    async def get_available_items_services(cls, query_db: AsyncSession, keyword: str | None = None):
        items = await AstInventoryDao.get_available_item_list(query_db, keyword)
        item_ids = [item.id for item in items]
        skus = await AstInventoryDao.get_item_skus_by_item_ids(query_db, item_ids)
        skus_map = defaultdict(list)
        for sku in skus:
            skus_map[sku.item_id].append(sku)
        result = []
        for item in items:
            item_dict = CamelCaseUtil.transform_result(item)
            cls.format_item_row(item_dict, skus_map.get(item.id, []))
            result.append(item_dict)
        return result

    @classmethod
    def format_purchase_order_row(cls, order_row: dict):
        if not order_row:
            return None
        order_row['businessNo'] = order_row.get('orderNo')
        order_row['paymentMethodLabel'] = cls.PAYMENT_METHOD_LABELS.get(
            order_row.get('paymentMethod'), order_row.get('paymentMethod') or '-'
        )
        order_row['statusLabel'] = cls.PURCHASE_STATUS_LABELS.get(order_row.get('status'), order_row.get('status'))
        return order_row

    @classmethod
    def format_stock_record_row(cls, record_row: dict, purchase_order_map: dict | None = None):
        purchase_order_map = purchase_order_map or {}
        quantity = cls.to_int(record_row.get('quantity'), 0)
        source_type = record_row.get('sourceType')
        source_id = record_row.get('sourceId')
        purchase_order = purchase_order_map.get(source_id) if source_type == 'purchase' else None
        record_row['stockDate'] = record_row.get('createTime') or record_row.get('recordDate')
        record_row['roleType'] = record_row.get('relatedType')
        record_row['roleName'] = record_row.get('relatedName')
        record_row['roleTypeLabel'] = cls.ROLE_TYPE_LABELS.get(record_row.get('roleType'), record_row.get('roleType') or '-')
        record_row['businessTypeLabel'] = cls.BUSINESS_TYPE_LABELS.get(
            record_row.get('businessType'), record_row.get('businessType') or '-'
        )
        record_row['stockType'] = 'in' if quantity > 0 else 'out'
        record_row['stockTypeLabel'] = '入库' if quantity > 0 else '出库'
        record_row['recordStatus'] = 'voided' if cls.to_int(record_row.get('delFlag'), 0) == 1 else 'normal'
        record_row['recordStatusLabel'] = '已作废' if record_row['recordStatus'] == 'voided' else '正常'
        record_row['businessNo'] = purchase_order.order_no if purchase_order else record_row.get('recordNo')
        record_row['operator'] = record_row.get('operatorName')
        record_row['specText'] = record_row.get('skuName')
        if purchase_order:
            record_row['purchaseOrderId'] = purchase_order.id
            record_row['purchaseOrderNo'] = purchase_order.order_no
        return record_row

    @classmethod
    async def export_stock_record_list_services(cls, stock_record_list: list):
        mapping_dict = {
            'recordNo': '流水号',
            'stockDate': '出入库时间',
            'itemName': '物品名称',
            'skuName': '规格',
            'businessType': '业务类型',
            'quantity': '数量',
            'stockBefore': '操作前库存',
            'stockAfter': '操作后库存',
            'roleType': '角色类型',
            'roleName': '角色名称',
            'operator': '经办人',
            'remark': '备注',
        }
        business_type_map = {
            'purchase': '采购',
            'receive': '领用',
            'return': '退领',
            'inventory': '盘点',
        }
        role_type_map = {
            'teacher': '员工',
            'staff': '员工',
            'student': '学员',
            'other': '其他',
            'admin': '其他',
        }
        for item in stock_record_list:
            item['businessType'] = business_type_map.get(item.get('businessType'), item.get('businessType'))
            item['roleType'] = role_type_map.get(item.get('roleType'), item.get('roleType'))
        return ExcelUtil.export_list2excel(stock_record_list, mapping_dict)

    @classmethod
    async def get_stock_record_list_services(
        cls, query_db: AsyncSession, query_object: AstStockRecordPageQueryModel, is_page: bool = False
    ):
        page_result = await AstInventoryDao.get_stock_record_list(query_db, query_object, is_page)
        rows = page_result.rows if hasattr(page_result, 'rows') else page_result
        purchase_order_ids = [
            row.get('sourceId')
            for row in rows
            if row.get('sourceType') == 'purchase' and row.get('sourceId')
        ]
        purchase_orders = await AstInventoryDao.get_purchase_orders_by_ids(query_db, list(set(purchase_order_ids)))
        purchase_order_map = {order.id: order for order in purchase_orders}
        if hasattr(page_result, 'rows'):
            page_result.rows = [cls.format_stock_record_row(row, purchase_order_map) for row in page_result.rows]
        else:
            page_result = [cls.format_stock_record_row(row, purchase_order_map) for row in page_result]
        return page_result

    @classmethod
    async def get_stock_record_summary_services(cls, query_db: AsyncSession, query_object: AstStockRecordPageQueryModel):
        total_count, in_total, out_total, net_total = await AstInventoryDao.get_stock_record_summary(query_db, query_object)
        return {
            'currentCount': int(total_count or 0),
            'inTotal': int(in_total or 0),
            'outTotal': int(out_total or 0),
            'netTotal': int(net_total or 0),
        }

    @classmethod
    async def get_stock_record_detail_services(cls, query_db: AsyncSession, record_id: int):
        record = await AstInventoryDao.get_stock_record_by_id(query_db, record_id)
        if not record:
            raise ServiceException(message='出入库记录不存在')
        result = CamelCaseUtil.transform_result(record)
        purchase_order_map = {}
        if record.source_type == 'purchase' and record.source_id:
            order = await AstInventoryDao.get_purchase_order_by_id(query_db, record.source_id)
            order_items = await AstInventoryDao.get_purchase_order_items_by_order_id(query_db, record.source_id)
            purchase_order_map = {order.id: order} if order else {}
            result['purchaseOrder'] = cls.format_purchase_order_row(CamelCaseUtil.transform_result(order)) if order else None
            result['purchaseItems'] = CamelCaseUtil.transform_result(order_items)
            for item in result['purchaseItems']:
                item['specText'] = item.get('skuName')
                item['amount'] = item.get('totalAmount')
        cls.format_stock_record_row(result, purchase_order_map)
        return result

    @classmethod
    async def void_stock_record_services(cls, query_db: AsyncSession, record_id: int, current_user_name: str):
        record = await AstInventoryDao.get_stock_record_by_id(query_db, record_id)
        if not record:
            raise ServiceException(message='出入库记录不存在')
        if record.del_flag == 1:
            return CrudResponseModel(is_success=True, message='记录已作废')
        try:
            sku_item = await AstInventoryDao.get_sku_with_item_by_id(query_db, record.sku_id)
            if not sku_item:
                raise ServiceException(message='关联SKU不存在，无法作废')
            sku, item = sku_item
            stock_after_void = (sku.stock or 0) - (record.quantity or 0)
            await AstInventoryDao.update_item_sku_dao(
                query_db,
                sku.id,
                {
                    'stock': stock_after_void,
                    'available_stock': stock_after_void,
                    'update_by': current_user_name,
                    'update_time': datetime.now(),
                },
            )
            await AstInventoryDao.update_stock_record_dao(
                query_db,
                record.id,
                {
                    'del_flag': 1,
                    'remark': f"{record.remark or ''} 作废人:{current_user_name}".strip(),
                },
            )
            await AstInventoryDao.refresh_item_stock_dao(query_db, item.id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='作废成功，库存已回滚')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_purchase_import_template_services(cls):
        headers = ['物品名称', '物品规格', '采购单价', '采购数量', '支付方式', '账户', '年度账本', '采购日期', '采购备注', '明细备注']
        selector_headers = ['支付方式']
        option_list = [{'支付方式': ['现金', '微信', '支付宝', '银行卡', 'POS机', '转账']}]
        return ExcelUtil.get_excel_template(headers, selector_headers, option_list)

    @classmethod
    def normalize_import_value(cls, value):
        if pd.isna(value):
            return None
        value = str(value).strip()
        return value if value else None

    @classmethod
    async def import_purchase_services(cls, query_db: AsyncSession, file, current_user_name: str):
        file_bytes = await file.read()
        if not file_bytes:
            raise ServiceException(message='导入文件为空')
        try:
            data_frame = pd.read_excel(io.BytesIO(file_bytes))
        except Exception as e:
            raise ServiceException(message=f'读取Excel失败：{str(e)}')
        required_headers = ['物品名称', '采购单价', '采购数量']
        for header in required_headers:
            if header not in data_frame.columns:
                raise ServiceException(message=f'导入失败，缺少列：{header}')

        payment_method_reverse = {label: key for key, label in cls.PAYMENT_METHOD_LABELS.items()}
        items = []
        first_row = data_frame.iloc[0] if not data_frame.empty else None
        if first_row is None:
            raise ServiceException(message='导入文件没有明细数据')
        for index, row in data_frame.iterrows():
            item_name = cls.normalize_import_value(row.get('物品名称'))
            sku_name = cls.normalize_import_value(row.get('物品规格'))
            if not item_name:
                continue
            sku_item = await AstInventoryDao.get_sku_by_item_name_and_sku_name(query_db, item_name, sku_name)
            if not sku_item:
                raise ServiceException(message=f'第{index + 2}行物品或规格不存在：{item_name} {sku_name or ""}'.strip())
            sku, item = sku_item
            quantity_value = cls.normalize_import_value(row.get('采购数量'))
            quantity = cls.to_int(quantity_value, 0)
            if quantity <= 0:
                raise ServiceException(message=f'第{index + 2}行采购数量必须大于0')
            unit_price = cls.to_decimal(cls.normalize_import_value(row.get('采购单价')), 0)
            items.append(
                AstStockOperationItemModel(
                    skuId=sku.id,
                    itemId=item.id,
                    itemName=item.item_name,
                    skuName=sku.sku_name,
                    specText=sku.sku_name,
                    quantity=quantity,
                    unitPrice=unit_price,
                    remark=cls.normalize_import_value(row.get('明细备注')),
                )
            )
        if not items:
            raise ServiceException(message='导入文件没有有效采购明细')

        payment_method_text = cls.normalize_import_value(first_row.get('支付方式'))
        purchase_form = AddPurchaseOrderModel(
            purchaseDate=cls.normalize_import_value(first_row.get('采购日期')) or date.today(),
            paymentMethod=payment_method_reverse.get(payment_method_text, payment_method_text),
            accountName=cls.normalize_import_value(first_row.get('账户')),
            yearBook=cls.normalize_import_value(first_row.get('年度账本')),
            operatorName=current_user_name,
            remark=cls.normalize_import_value(first_row.get('采购备注')),
            items=items,
        )
        return await cls.create_purchase_services(query_db, purchase_form, current_user_name)

    @classmethod
    async def apply_stock_change(
        cls,
        query_db: AsyncSession,
        *,
        sku_id: int,
        quantity: int,
        business_type: str,
        source_type: str,
        source_id: int | None,
        related_type: str | None,
        related_name: str | None,
        operator_name: str | None,
        record_date: date,
        create_by: str,
        remark: str | None = None,
        actual_stock: int | None = None,
    ):
        sku_item = await AstInventoryDao.get_sku_with_item_by_id(query_db, sku_id)
        if not sku_item:
            raise ServiceException(message=f'SKU({sku_id})不存在')
        sku, item = sku_item
        stock_before = sku.stock or 0
        if actual_stock is not None:
            stock_after = actual_stock
            quantity = stock_after - stock_before
        else:
            stock_after = stock_before + quantity

        await AstInventoryDao.update_item_sku_dao(
            query_db,
            sku.id,
            {
                'stock': stock_after,
                'available_stock': stock_after,
                'update_by': create_by,
                'update_time': datetime.now(),
            },
        )
        record = AstItemStockRecord(
            record_no=cls.make_no('SR'),
            item_id=item.id,
            item_name=item.item_name,
            sku_id=sku.id,
            sku_name=sku.sku_name,
            business_type=business_type,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            source_type=source_type,
            source_id=source_id,
            related_name=related_name,
            related_type=related_type,
            operator_name=operator_name,
            record_date=record_date,
            create_by=create_by,
            create_time=datetime.now(),
            remark=remark,
        )
        await AstInventoryDao.add_stock_record_dao(query_db, record)
        await AstInventoryDao.refresh_item_stock_dao(query_db, item.id)
        return record

    @classmethod
    async def create_purchase_services(
        cls, query_db: AsyncSession, page_object: AddPurchaseOrderModel, current_user_name: str
    ):
        if not page_object.items:
            raise ServiceException(message='请选择采购物品')
        try:
            purchase_date = cls.parse_date(page_object.purchase_date)
            order = AstPurchaseOrder(
                order_no=cls.make_no('PO'),
                purchase_date=purchase_date,
                supplier_name=page_object.supplier_name,
                payment_method=page_object.payment_method,
                account_name=page_object.account_name or page_object.account,
                year_book=page_object.year_book,
                status=1,
                operator_name=page_object.operator_name or page_object.operator or current_user_name,
                create_by=current_user_name,
                create_time=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now(),
                remark=page_object.remark,
            )
            order = await AstInventoryDao.add_purchase_order_dao(query_db, order)

            total_quantity = 0
            total_amount = Decimal('0')
            for item_detail in page_object.items:
                quantity = cls.to_int(item_detail.quantity, 0)
                if quantity <= 0:
                    raise ServiceException(message='采购数量必须大于0')
                sku_item = await AstInventoryDao.get_sku_with_item_by_id(query_db, item_detail.sku_id)
                if not sku_item:
                    raise ServiceException(message=f'SKU({item_detail.sku_id})不存在')
                sku, item = sku_item
                unit_price = cls.to_decimal(item_detail.unit_price if item_detail.unit_price is not None else item_detail.price, 0)
                item_amount = unit_price * quantity
                total_quantity += quantity
                total_amount += item_amount
                order_item = AstPurchaseOrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    item_name=item.item_name,
                    sku_id=sku.id,
                    sku_name=sku.sku_name,
                    unit_price=unit_price,
                    quantity=quantity,
                    total_amount=item_amount,
                    create_by=current_user_name,
                    create_time=datetime.now(),
                    remark=item_detail.remark,
                )
                await AstInventoryDao.add_purchase_order_item_dao(query_db, order_item)
                await AstInventoryDao.update_item_sku_dao(
                    query_db,
                    sku.id,
                    {
                        'cost_price': unit_price,
                        'update_by': current_user_name,
                        'update_time': datetime.now(),
                    },
                )
                await cls.apply_stock_change(
                    query_db,
                    sku_id=sku.id,
                    quantity=quantity,
                    business_type='purchase',
                    source_type='purchase',
                    source_id=order.id,
                    related_type='admin',
                    related_name=order.operator_name,
                    operator_name=order.operator_name,
                    record_date=purchase_date,
                    create_by=current_user_name,
                    remark=item_detail.remark or '采购入库',
                )

            await query_db.execute(
                AstPurchaseOrder.__table__.update()
                .where(AstPurchaseOrder.id == order.id)
                .values(total_quantity=total_quantity, total_amount=total_amount)
            )
            order_id = order.id
            order_no = order.order_no
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='采购成功', result={'id': order_id, 'orderNo': order_no})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def create_receive_services(
        cls, query_db: AsyncSession, page_object: AddReceiveStockModel, current_user_name: str
    ):
        if not page_object.items:
            raise ServiceException(message='请选择领用物品')
        try:
            record_date = cls.parse_date(page_object.receive_time)
            operator = page_object.operator or current_user_name
            for item_detail in page_object.items:
                quantity = cls.to_int(item_detail.quantity, 0)
                if quantity <= 0:
                    raise ServiceException(message='领用数量必须大于0')
                await cls.apply_stock_change(
                    query_db,
                    sku_id=item_detail.sku_id,
                    quantity=-quantity,
                    business_type='receive',
                    source_type='receive',
                    source_id=None,
                    related_type=page_object.role_type,
                    related_name=page_object.role_name,
                    operator_name=operator,
                    record_date=record_date,
                    create_by=current_user_name,
                    remark=item_detail.remark or page_object.remark or '领用出库',
                )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='领用成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def create_return_services(
        cls, query_db: AsyncSession, page_object: AddReturnStockModel, current_user_name: str
    ):
        if not page_object.items:
            raise ServiceException(message='请选择退领物品')
        try:
            record_date = cls.parse_date(page_object.return_time)
            operator = page_object.operator or current_user_name
            for item_detail in page_object.items:
                quantity = cls.to_int(item_detail.quantity, 0)
                if quantity <= 0:
                    raise ServiceException(message='退领数量必须大于0')
                await cls.apply_stock_change(
                    query_db,
                    sku_id=item_detail.sku_id,
                    quantity=quantity,
                    business_type='return',
                    source_type='return',
                    source_id=None,
                    related_type=page_object.role_type,
                    related_name=page_object.role_name,
                    operator_name=operator,
                    record_date=record_date,
                    create_by=current_user_name,
                    remark=item_detail.remark or page_object.remark or '退领入库',
                )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='退领成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def create_inventory_services(
        cls, query_db: AsyncSession, page_object: AddInventoryStockModel, current_user_name: str
    ):
        if not page_object.items:
            raise ServiceException(message='请选择盘点物品')
        try:
            record_date = cls.parse_date(page_object.inventory_date)
            operator = page_object.operator or current_user_name
            for item_detail in page_object.items:
                actual_stock = item_detail.actual_stock
                if actual_stock is None:
                    actual_stock = item_detail.current_stock
                if actual_stock is None:
                    raise ServiceException(message='请填写盘点库存')
                await cls.apply_stock_change(
                    query_db,
                    sku_id=item_detail.sku_id,
                    quantity=0,
                    business_type='inventory',
                    source_type='inventory',
                    source_id=None,
                    related_type='admin',
                    related_name=operator,
                    operator_name=operator,
                    record_date=record_date,
                    create_by=current_user_name,
                    remark=item_detail.remark or page_object.remark or '库存盘点',
                    actual_stock=actual_stock,
                )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='盘点成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    def build_fee_row(cls, fee_row: dict, courses):
        course_ids = [course.course_id for course in courses]
        course_names = [course.course_name for course in courses if course.course_name]
        fee_row['price'] = fee_row.get('amount')
        fee_row['onlineSale'] = fee_row.get('onlineSale') if fee_row.get('onlineSale') is not None else 0
        fee_row['courseIds'] = course_ids
        fee_row['courseNames'] = course_names
        fee_row['courseName'] = '、'.join(course_names)
        fee_row['courses'] = [CamelCaseUtil.transform_result(course) for course in courses]
        return fee_row

    @classmethod
    async def attach_fee_courses(cls, query_db: AsyncSession, fee_rows):
        fee_ids = [row.get('id') for row in fee_rows if row.get('id')]
        courses = await AstInventoryDao.get_fee_courses_by_fee_ids(query_db, fee_ids)
        course_map = defaultdict(list)
        for course in courses:
            course_map[course.fee_id].append(course)
        return [cls.build_fee_row(row, course_map.get(row.get('id'), [])) for row in fee_rows]

    @classmethod
    async def get_fee_list_services(
        cls, query_db: AsyncSession, query_object: AstFeeItemPageQueryModel, is_page: bool = False
    ):
        page_result = await AstInventoryDao.get_fee_list(query_db, query_object, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = await cls.attach_fee_courses(query_db, page_result.rows)
        else:
            page_result = await cls.attach_fee_courses(query_db, page_result)
        return page_result

    @classmethod
    async def get_fee_detail_services(cls, query_db: AsyncSession, fee_id: int):
        fee = await AstInventoryDao.get_fee_by_id(query_db, fee_id)
        if not fee:
            raise ServiceException(message='费用不存在')
        rows = await cls.attach_fee_courses(query_db, [CamelCaseUtil.transform_result(fee)])
        return rows[0]

    @classmethod
    def get_fee_amount(cls, page_object):
        return cls.to_decimal(page_object.amount if page_object.amount is not None else page_object.price, 0)

    @classmethod
    def build_fee_courses(cls, fee_id: int, page_object, current_user_name: str):
        result = []
        if page_object.courses:
            for course in page_object.courses:
                result.append({'course_id': course.course_id, 'course_name': course.course_name})
        else:
            course_ids = page_object.course_ids or []
            course_names = page_object.course_names or []
            for index, course_id in enumerate(course_ids):
                result.append(
                    {
                        'course_id': course_id,
                        'course_name': course_names[index] if index < len(course_names) else None,
                    }
                )
        seen = set()
        courses = []
        for course in result:
            if course['course_id'] in seen:
                continue
            seen.add(course['course_id'])
            courses.append(
                AstFeeCourse(
                    fee_id=fee_id,
                    course_id=course['course_id'],
                    course_name=course['course_name'],
                    create_by=current_user_name,
                    create_time=datetime.now(),
                )
            )
        return courses

    @classmethod
    async def save_fee_courses(cls, query_db: AsyncSession, fee_id: int, page_object, current_user_name: str):
        await AstInventoryDao.delete_fee_courses_by_fee_id(query_db, fee_id)
        for fee_course in cls.build_fee_courses(fee_id, page_object, current_user_name):
            await AstInventoryDao.add_fee_course_dao(query_db, fee_course)

    @classmethod
    async def add_fee_services(cls, query_db: AsyncSession, page_object: AddAstFeeItemModel, current_user_name: str):
        try:
            fee = AstFeeItem(
                fee_name=page_object.fee_name,
                amount=cls.get_fee_amount(page_object),
                online_sale=page_object.online_sale or 0,
                status=page_object.status,
                sort=page_object.sort or 0,
                create_by=current_user_name,
                create_time=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now(),
                remark=page_object.remark,
            )
            fee = await AstInventoryDao.add_fee_dao(query_db, fee)
            fee_id = fee.id
            await cls.save_fee_courses(query_db, fee.id, page_object, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': fee_id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_fee_services(cls, query_db: AsyncSession, page_object: EditAstFeeItemModel, current_user_name: str):
        fee = await AstInventoryDao.get_fee_by_id(query_db, page_object.id)
        if not fee:
            raise ServiceException(message='费用不存在')
        try:
            await AstInventoryDao.update_fee_dao(
                query_db,
                page_object.id,
                {
                    'fee_name': page_object.fee_name,
                    'amount': cls.get_fee_amount(page_object),
                    'online_sale': page_object.online_sale or 0,
                    'status': page_object.status,
                    'sort': page_object.sort or 0,
                    'update_by': current_user_name,
                    'update_time': datetime.now(),
                    'remark': page_object.remark,
                },
            )
            await cls.save_fee_courses(query_db, page_object.id, page_object, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def change_fee_status_services(
        cls, query_db: AsyncSession, page_object: ChangeAstFeeStatusModel, current_user_name: str
    ):
        try:
            await AstInventoryDao.update_fee_dao(
                query_db,
                page_object.id,
                {'status': page_object.status, 'update_by': current_user_name, 'update_time': datetime.now()},
            )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='状态修改成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_fee_services(cls, query_db: AsyncSession, page_object: DeleteAstFeeItemModel, current_user_name: str):
        if not page_object.fee_ids:
            raise ServiceException(message='传入费用id为空')
        try:
            for fee_id in page_object.fee_ids.split(','):
                await AstInventoryDao.delete_fee_dao(query_db, int(fee_id), current_user_name)
                await AstInventoryDao.delete_fee_courses_by_fee_id(query_db, int(fee_id))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e
