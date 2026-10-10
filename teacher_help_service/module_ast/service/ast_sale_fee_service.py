import re
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_ast.dao.ast_inventory_dao import AstInventoryDao
from module_ast.dao.ast_sale_fee_dao import AstSaleFeeDao
from module_ast.entity.do.ast_fee_course_do import AstFeeCourse
from module_ast.entity.do.ast_fee_item_do import AstFeeItem
from module_teach.service.teach_import_util import ImportRowError, TeachImportUtil
from utils.common_util import CamelCaseUtil


class AstSaleFeeService:
    """
    物品费用：销售订单详情（报名/续费订单中的物品销售出库）、费用 Excel 导入
    """

    ORDER_TYPE_LABELS = {'enroll': '报名', 'renew': '续费', 'transfer': '转课', 'import': '导入'}
    ORDER_STATUS_LABELS = {'pending': '待支付', 'paid': '已支付'}
    ITEM_TYPE_LABELS = {'course': '课程', 'item': '物品', 'fee': '费用'}
    FEE_HEADERS = ['*费用名称', '*金额', '线上售卖', '状态', '排序', '关联课程', '备注']
    FEE_REQUIRED = ['费用名称', '金额']
    COURSE_SPLIT = re.compile(r'[,，、;；\n]+')

    @classmethod
    def mask_phone(cls, phone: str | None):
        if not phone or len(phone) < 7:
            return phone or ''
        return f'{phone[:3]}****{phone[-4:]}'

    # ------------------------------------------------------------------ 销售订单详情

    @classmethod
    async def get_sale_order_detail_services(cls, query_db: AsyncSession, order_id: int):
        order = await AstSaleFeeDao.get_order(query_db, order_id)
        if not order:
            raise ServiceException(message='销售订单不存在或已删除')
        items = await AstSaleFeeDao.get_order_items(query_db, order_id)
        records = await AstSaleFeeDao.get_order_stock_records(query_db, order_id)
        order_row = CamelCaseUtil.transform_result(order)
        order_row['parentPhone'] = cls.mask_phone(order.parent_phone)
        order_row['orderTypeName'] = cls.ORDER_TYPE_LABELS.get(order.order_type, order.order_type)
        order_row['statusName'] = cls.ORDER_STATUS_LABELS.get(order.status, order.status)
        order_row['arrearsAmount'] = max(
            (order.receivable_amount or Decimal('0')) - (order.paid_amount or Decimal('0')), Decimal('0')
        )
        item_rows = []
        for item in items:
            row = CamelCaseUtil.transform_result(item)
            row['itemTypeName'] = cls.ITEM_TYPE_LABELS.get(item.item_type, item.item_type)
            item_rows.append(row)
        record_rows = []
        for record in records:
            row = CamelCaseUtil.transform_result(record)
            row['stockTypeLabel'] = '入库' if (record.quantity or 0) > 0 else '出库'
            row['recordStatusLabel'] = '已作废' if record.del_flag == 1 else '正常'
            record_rows.append(row)
        return {
            'order': order_row,
            'items': item_rows,
            'goodsItems': [row for row in item_rows if row.get('itemType') == 'item'],
            'stockRecords': record_rows,
        }

    # ------------------------------------------------------------------ 费用导入

    @classmethod
    def get_fee_template_services(cls):
        return TeachImportUtil.build_template(
            '费用导入',
            cls.FEE_HEADERS,
            [
                '1. 表头带 * 的列必填；第2行为示例，导入前请删除。',
                '2. 费用名称不能与系统中已有费用重复，也不能在本文件中重复（不做覆盖更新）。',
                '3. 金额为大于等于0的数字，最多两位小数。',
                '4. 线上售卖填“是/否”，默认否；状态填“启用/停用”，默认启用；排序为整数，默认0。',
                '5. 关联课程填课程名称，多个用逗号或顿号分隔，须与课程管理中的名称完全一致且唯一；可不填。',
                '6. 整表校验：任一行有错误则整批不导入，并返回错误行。单次最多2000行。',
            ],
            options={'线上售卖': ['是', '否'], '状态': ['启用', '停用']},
            example=['教材费', '120', '否', '启用', '0', '少儿英语、少儿美术', '示例行，导入前删除'],
        )

    @classmethod
    def parse_flag(cls, values: dict, name: str, yes: str, no: str, default: int):
        value = values.get(name)
        if not value:
            return default
        if value == yes:
            return 1
        if value == no:
            return 0
        raise ImportRowError(f'{name}只能填“{yes}”或“{no}”')

    @classmethod
    async def import_fee_services(cls, query_db: AsyncSession, file, operator: str):
        rows = await TeachImportUtil.read_rows(file, cls.FEE_REQUIRED)
        existing_names = await AstSaleFeeDao.get_fee_names(query_db)
        course_map: dict[str, list] = {}
        for course in await AstSaleFeeDao.get_courses(query_db):
            course_map.setdefault(course.course_name, []).append(course)
        errors = []
        parsed = []
        file_names = set()
        for row_no, values in rows:
            try:
                fee_name = TeachImportUtil.required(values, '费用名称')
                if len(fee_name) > 100:
                    raise ImportRowError('费用名称不能超过100个字')
                if fee_name in existing_names:
                    raise ImportRowError(f'费用“{fee_name}”已存在')
                if fee_name in file_names:
                    raise ImportRowError(f'费用“{fee_name}”在文件中重复')
                file_names.add(fee_name)
                amount = TeachImportUtil.parse_money(values, '金额', required=True)
                if amount >= Decimal('100000000'):
                    raise ImportRowError('金额过大')
                online_sale = cls.parse_flag(values, '线上售卖', '是', '否', 0)
                status = cls.parse_flag(values, '状态', '启用', '停用', 1)
                sort = TeachImportUtil.parse_int(values, '排序', default=0)
                courses = []
                course_names = cls.COURSE_SPLIT.split(values.get('关联课程') or '')
                for name in [item.strip() for item in course_names if item.strip()]:
                    matched = course_map.get(name) or []
                    if not matched:
                        raise ImportRowError(f'关联课程“{name}”不存在')
                    if len(matched) > 1:
                        raise ImportRowError(f'关联课程“{name}”存在同名课程，无法确定')
                    if matched[0].id not in [course.id for course in courses]:
                        courses.append(matched[0])
                remark = values.get('备注')
                if remark and len(remark) > 500:
                    raise ImportRowError('备注不能超过500个字')
                parsed.append((fee_name, amount, online_sale, status, sort, courses, remark))
            except ImportRowError as e:
                errors.append({'row': row_no, 'message': str(e)})
        if errors:
            return TeachImportUtil.result(len(rows), errors)
        try:
            now = datetime.now()
            for fee_name, amount, online_sale, status, sort, courses, remark in parsed:
                fee = await AstInventoryDao.add_fee_dao(
                    query_db,
                    AstFeeItem(
                        fee_name=fee_name,
                        amount=amount,
                        online_sale=online_sale,
                        status=status,
                        sort=sort,
                        create_by=operator,
                        create_time=now,
                        update_by=operator,
                        update_time=now,
                        remark=remark,
                    ),
                )
                for course in courses:
                    await AstInventoryDao.add_fee_course_dao(
                        query_db,
                        AstFeeCourse(
                            fee_id=fee.id,
                            course_id=course.id,
                            course_name=course.course_name,
                            create_by=operator,
                            create_time=now,
                        ),
                    )
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise e
        return TeachImportUtil.result(len(rows), [], success_count=len(parsed))
