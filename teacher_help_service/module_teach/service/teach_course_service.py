from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_course_dao import TeachCourseDao
from module_teach.entity.do.teach_course_package_do import TeachCoursePackage
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_package_item_do import TeachPackageItem
from module_teach.entity.do.teach_course_price_do import TeachCoursePrice
from module_teach.entity.vo.teach_course_vo import (
    AddTeachCourseModel,
    AddTeachCoursePackageModel,
    BatchAddTeachCourseModel,
    ChangeTeachCourseStatusModel,
    ChangeTeachPackageStatusModel,
    DeleteTeachCoursePackageModel,
    DeleteTeachCourseModel,
    EditTeachCourseModel,
    EditTeachCoursePackageModel,
    TeachCoursePackagePageQueryModel,
    TeachCoursePageQueryModel,
)
from exceptions.exception import ServiceException
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class TeachCourseService:
    """
    课程管理模块服务层
    """

    COURSE_TYPE_LABELS = {
        'one_to_many': '一对多',
        'one_to_one': '一对一',
    }
    CHARGE_TYPE_LABELS = {
        'class': '按课时',
        'month': '按月',
        'day': '按天',
    }
    CHARGE_UNITS = {
        'class': '课时',
        'month': '月',
        'day': '天',
    }
    PACKAGE_ITEM_TYPE_LABELS = {
        'course': '课程',
        'item': '物品',
        'fee': '费用',
    }
    GRADE_LABELS = {
        '1': '一年级',
        '2': '二年级',
        '3': '三年级',
        '4': '四年级',
        '5': '五年级',
        '6': '六年级',
        '7': '初一',
        '8': '初二',
        '9': '初三',
        '10': '高一',
        '11': '高二',
        '12': '高三',
    }
    SUBJECT_LABELS = {
        '1': '语文',
        '2': '数学',
        '3': '英语',
        '4': '物理',
        '5': '化学',
        '6': '生物',
        '7': '政治',
        '8': '历史',
        '9': '地理',
    }
    SEMESTER_LABELS = {
        '1': '春季',
        '2': '暑假',
        '3': '秋季',
        '4': '寒假',
    }

    @classmethod
    def make_no(cls):
        return f'COURSE{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def make_package_no(cls):
        return f'PKG{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

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
    def normalize_course_type(cls, value):
        type_value = str(value or 'one_to_many')
        if type_value in ['1', 'oneToMany', 'one_to_many', '一对多']:
            return 'one_to_many'
        if type_value in ['2', 'oneToOne', 'one_to_one', '一对一']:
            return 'one_to_one'
        return type_value

    @classmethod
    def fill_labels(cls, page_object):
        page_object.course_type = cls.normalize_course_type(page_object.course_type)
        if page_object.grade and not page_object.grade_label:
            page_object.grade_label = cls.GRADE_LABELS.get(str(page_object.grade), page_object.grade)
        if page_object.subject and not page_object.subject_label:
            page_object.subject_label = cls.SUBJECT_LABELS.get(str(page_object.subject), page_object.subject)
        if page_object.semester and not page_object.semester_label:
            page_object.semester_label = cls.SEMESTER_LABELS.get(str(page_object.semester), page_object.semester)

    @classmethod
    def get_raw_value(cls, raw, *names, default=None):
        for name in names:
            if isinstance(raw, dict):
                if name in raw:
                    return raw.get(name)
            else:
                value = getattr(raw, name, None)
                if value is not None:
                    return value
        return default

    @classmethod
    def normalize_price(cls, raw, charge_type: str, index: int, page_object=None):
        price_name = cls.get_raw_value(raw, 'price_name', 'priceName', 'name', default='单价') or '单价'
        quantity = max(cls.to_int(cls.get_raw_value(raw, 'quantity', default=1), 1), 1)
        total_price = cls.to_decimal(cls.get_raw_value(raw, 'total_price', 'totalPrice', default=0), 0)
        raw_unit_price = cls.get_raw_value(raw, 'unit_price', 'unitPrice', default=None)
        unit_price = cls.to_decimal(raw_unit_price, 0) if raw_unit_price not in [None, ''] else total_price / quantity
        return {
            'charge_type': charge_type,
            'price_name': price_name,
            'quantity': quantity,
            'total_price': total_price,
            'unit_price': unit_price,
            'deduct_rule': cls.get_raw_value(raw, 'deduct_rule', 'deductRule', default=getattr(page_object, 'class_deduct_rule', None)),
            'absence_rule': cls.get_raw_value(raw, 'absence_rule', 'absenceRule', default=getattr(page_object, 'class_absence_rule', None)),
            'sort': cls.to_int(cls.get_raw_value(raw, 'sort', default=index), index),
            'status': cls.to_int(cls.get_raw_value(raw, 'status', default=1), 1),
        }

    @classmethod
    def build_price_payloads(cls, page_object):
        payloads = []
        raw_prices = getattr(page_object, 'prices', None) or []
        for index, price in enumerate(raw_prices):
            charge_type = cls.get_raw_value(price, 'charge_type', 'chargeType', default='class') or 'class'
            payloads.append(cls.normalize_price(price, charge_type, index, page_object))

        section_map = [
            ('class', getattr(page_object, 'charge_by_class', False), getattr(page_object, 'class_prices', None) or []),
            ('month', getattr(page_object, 'charge_by_month', False), getattr(page_object, 'month_prices', None) or []),
            ('day', getattr(page_object, 'charge_by_day', False), getattr(page_object, 'day_prices', None) or []),
        ]
        for charge_type, enabled, prices in section_map:
            if not enabled:
                continue
            for index, price in enumerate(prices):
                payloads.append(cls.normalize_price(price, charge_type, index, page_object))

        deduped = []
        seen = set()
        for index, price in enumerate(payloads):
            key = (price['charge_type'], price['price_name'], price['quantity'], str(price['total_price']))
            if key in seen:
                continue
            seen.add(key)
            price['sort'] = index
            deduped.append(price)
        return deduped

    @classmethod
    def validate_course_prices(cls, page_object):
        price_payloads = cls.build_price_payloads(page_object)
        if not price_payloads:
            raise ServiceException(message='请至少开启一种收费方式')
        invalid_price = next(
            (
                price
                for price in price_payloads
                if not price['price_name'] or not price['quantity'] or price['total_price'] <= 0
            ),
            None,
        )
        if invalid_price:
            raise ServiceException(message='课程定价名称、数量和总价不能为空')
        return price_payloads

    @classmethod
    def build_course_do(cls, page_object, current_user_name: str):
        cls.fill_labels(page_object)
        now = datetime.now()
        return TeachCourse(
            course_no=page_object.course_no or cls.make_no(),
            course_name=page_object.course_name,
            course_type=page_object.course_type,
            schedule_color=page_object.schedule_color or '#409EFF',
            grade=page_object.grade,
            grade_label=page_object.grade_label,
            subject=page_object.subject,
            subject_label=page_object.subject_label,
            semester=page_object.semester,
            semester_label=page_object.semester_label,
            student_count=page_object.student_count or 0,
            online_sale=page_object.online_sale or 0,
            status=page_object.status if page_object.status is not None else 1,
            create_by=current_user_name,
            create_time=now,
            update_by=current_user_name,
            update_time=now,
            remark=page_object.remark,
        )

    @classmethod
    async def save_prices(cls, query_db: AsyncSession, course_id: int, page_object, current_user_name: str):
        await TeachCourseDao.delete_prices_by_course_id(query_db, course_id, current_user_name)
        now = datetime.now()
        for price in cls.validate_course_prices(page_object):
            await TeachCourseDao.add_teach_course_price(
                query_db,
                TeachCoursePrice(
                    course_id=course_id,
                    charge_type=price['charge_type'],
                    price_name=price['price_name'],
                    quantity=price['quantity'],
                    total_price=price['total_price'],
                    unit_price=price['unit_price'],
                    deduct_rule=price['deduct_rule'],
                    absence_rule=price['absence_rule'],
                    sort=price['sort'],
                    status=price['status'],
                    create_by=current_user_name,
                    create_time=now,
                    update_by=current_user_name,
                    update_time=now,
                ),
            )

    @classmethod
    def fmt_money(cls, value):
        decimal_value = cls.to_decimal(value, 0).quantize(Decimal('0.01'))
        text = format(decimal_value, 'f').rstrip('0').rstrip('.')
        return text or '0'

    @classmethod
    def format_price_row(cls, price: TeachCoursePrice):
        charge_type = price.charge_type
        quantity = price.quantity or 1
        unit = cls.CHARGE_UNITS.get(charge_type, '')
        total_text = cls.fmt_money(price.total_price)
        unit_text = cls.fmt_money(price.unit_price)
        if quantity == 1:
            display = f'{price.price_name}({unit_text}元/{unit})'
        else:
            display = f'{price.price_name}({total_text}元{quantity}{unit})'
        return {
            'id': price.id,
            'courseId': price.course_id,
            'chargeType': charge_type,
            'chargeTypeName': cls.CHARGE_TYPE_LABELS.get(charge_type, charge_type),
            'priceName': price.price_name,
            'name': price.price_name,
            'quantity': quantity,
            'totalPrice': price.total_price,
            'unitPrice': price.unit_price,
            'deductRule': price.deduct_rule,
            'absenceRule': price.absence_rule,
            'sort': price.sort or 0,
            'status': price.status,
            'displayText': display,
        }

    @classmethod
    def format_course_row(cls, course_row: dict, prices: list[TeachCoursePrice]):
        price_rows = [cls.format_price_row(price) for price in prices]
        price_map = defaultdict(list)
        for price in price_rows:
            price_map[price['chargeType']].append(price)
        charge_types = [charge_type for charge_type in ['class', 'month', 'day'] if price_map.get(charge_type)]
        price_lines = [price['displayText'] for price in price_rows]
        course_type = course_row.get('courseType') or course_row.get('course_type')
        course_row['courseType'] = cls.normalize_course_type(course_type)
        course_row['courseTypeName'] = cls.COURSE_TYPE_LABELS.get(course_row['courseType'], course_row['courseType'])
        course_row['chargeTypes'] = charge_types
        course_row['chargeTypeText'] = '、'.join([cls.CHARGE_TYPE_LABELS.get(item, item) for item in charge_types]) or '未设置'
        course_row['priceLines'] = price_lines
        course_row['pricingSummary'] = '\n'.join(price_lines)
        course_row['priceStandard'] = '；'.join(price_lines)
        course_row['prices'] = price_rows
        course_row['classPrices'] = price_map.get('class', [])
        course_row['monthPrices'] = price_map.get('month', [])
        course_row['dayPrices'] = price_map.get('day', [])
        course_row['chargeByClass'] = bool(price_map.get('class'))
        course_row['chargeByMonth'] = bool(price_map.get('month'))
        course_row['chargeByDay'] = bool(price_map.get('day'))
        course_row['studentCount'] = course_row.get('studentCount') or 0
        course_row['onlineSale'] = course_row.get('onlineSale') or 0
        return course_row

    @classmethod
    async def attach_prices(cls, query_db: AsyncSession, course_rows):
        course_ids = [row.get('id') for row in course_rows if row.get('id')]
        prices = await TeachCourseDao.get_prices_by_course_ids(query_db, course_ids)
        price_map = defaultdict(list)
        for price in prices:
            price_map[price.course_id].append(price)
        return [cls.format_course_row(row, price_map.get(row.get('id'), [])) for row in course_rows]

    @classmethod
    async def get_teach_course_list_services(
        cls, query_db: AsyncSession, query_object: TeachCoursePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query_object.course_type = cls.normalize_course_type(query_object.course_type) if query_object.course_type else None
        page_result = await TeachCourseDao.get_teach_course_list(query_db, query_object, data_scope_sql, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = await cls.attach_prices(query_db, page_result.rows)
        else:
            page_result = await cls.attach_prices(query_db, page_result)
        return page_result

    @classmethod
    async def get_teach_course_detail_services(cls, query_db: AsyncSession, course_id: int):
        course = await TeachCourseDao.get_teach_course_by_id(query_db, course_id)
        if not course:
            raise ServiceException(message='课程不存在')
        prices = await TeachCourseDao.get_prices_by_course_id(query_db, course_id)
        return cls.format_course_row(CamelCaseUtil.transform_result(course), prices)

    @classmethod
    async def add_teach_course_services(cls, query_db: AsyncSession, page_object: AddTeachCourseModel, current_user_name: str):
        if page_object.course_no:
            exist = await TeachCourseDao.get_teach_course_by_no(query_db, page_object.course_no)
            if exist:
                raise ServiceException(message='课程编号已存在')
        try:
            course_id = await cls.create_course_with_prices(query_db, page_object, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': course_id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def create_course_with_prices(
        cls, query_db: AsyncSession, page_object: AddTeachCourseModel, current_user_name: str
    ):
        course = await TeachCourseDao.add_teach_course(query_db, cls.build_course_do(page_object, current_user_name))
        await cls.save_prices(query_db, course.id, page_object, current_user_name)
        return course.id

    @classmethod
    async def batch_add_teach_course_services(
        cls, query_db: AsyncSession, page_object: BatchAddTeachCourseModel, current_user_name: str
    ):
        courses = page_object.courses or []
        if not courses:
            raise ServiceException(message='请至少添加一门课程')
        course_nos = [course.course_no for course in courses if course.course_no]
        if len(course_nos) != len(set(course_nos)):
            raise ServiceException(message='课程编号不能重复')
        for course_no in course_nos:
            exist = await TeachCourseDao.get_teach_course_by_no(query_db, course_no)
            if exist:
                raise ServiceException(message=f'课程编号{course_no}已存在')
        try:
            course_ids = []
            for course in courses:
                course.validate_fields()
                course_ids.append(await cls.create_course_with_prices(query_db, course, current_user_name))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message=f'批量新增成功，共新增{len(course_ids)}门课程', result={'ids': course_ids})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_course_services(cls, query_db: AsyncSession, page_object: EditTeachCourseModel, current_user_name: str):
        course = await TeachCourseDao.get_teach_course_by_id(query_db, page_object.id)
        if not course:
            raise ServiceException(message='课程不存在')
        if page_object.course_no:
            exist = await TeachCourseDao.get_teach_course_by_no(query_db, page_object.course_no)
            if exist and exist.id != page_object.id:
                raise ServiceException(message='课程编号已存在')
        cls.fill_labels(page_object)
        try:
            course.course_no = page_object.course_no or course.course_no
            course.course_name = page_object.course_name
            course.course_type = page_object.course_type
            course.schedule_color = page_object.schedule_color or '#409EFF'
            course.grade = page_object.grade
            course.grade_label = page_object.grade_label
            course.subject = page_object.subject
            course.subject_label = page_object.subject_label
            course.semester = page_object.semester
            course.semester_label = page_object.semester_label
            course.student_count = page_object.student_count or 0
            course.online_sale = page_object.online_sale or 0
            course.status = page_object.status if page_object.status is not None else 1
            course.update_by = current_user_name
            course.remark = page_object.remark
            await TeachCourseDao.edit_teach_course(query_db, course)
            await cls.save_prices(query_db, course.id, page_object, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_course_services(cls, query_db: AsyncSession, page_object: DeleteTeachCourseModel, current_user_name: str):
        course_ids = [int(item) for item in page_object.course_ids.split(',') if item.strip()]
        if not course_ids:
            raise ServiceException(message='请选择要删除的课程')
        try:
            await TeachCourseDao.delete_teach_course(query_db, course_ids, current_user_name)
            for course_id in course_ids:
                await TeachCourseDao.delete_prices_by_course_id(query_db, course_id, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def change_course_status_services(
        cls, query_db: AsyncSession, page_object: ChangeTeachCourseStatusModel, current_user_name: str
    ):
        course = await TeachCourseDao.get_teach_course_by_id(query_db, page_object.id)
        if not course:
            raise ServiceException(message='课程不存在')
        try:
            await TeachCourseDao.update_teach_course_status(query_db, page_object.id, page_object.status, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='状态修改成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_course_options_services(cls, query_db: AsyncSession, keyword: str | None = None):
        courses = await TeachCourseDao.get_available_course_list(query_db, keyword)
        rows = CamelCaseUtil.transform_result(courses)
        rows = await cls.attach_prices(query_db, rows)
        return [
            {
                'id': row.get('id'),
                'courseName': row.get('courseName'),
                'courseType': row.get('courseTypeName'),
                'courseTypeValue': row.get('courseType'),
                'scheduleColor': row.get('scheduleColor'),
                'priceStandard': row.get('priceStandard') or '未设置',
                'prices': row.get('prices') or [],
                'status': row.get('status'),
            }
            for row in rows
        ]

    @classmethod
    def calc_package_item_amount(cls, item: dict):
        quantity = max(cls.to_int(item.get('quantity'), 1), 1)
        unit_price = cls.to_decimal(item.get('unit_price'), 0)
        total_price = unit_price * quantity
        raw_subtotal_price = item.get('subtotal_price')
        if raw_subtotal_price not in [None, '']:
            subtotal_price = cls.to_decimal(raw_subtotal_price, 0)
            if subtotal_price < 0:
                subtotal_price = Decimal('0')
            return quantity, total_price.quantize(Decimal('0.01')), subtotal_price.quantize(Decimal('0.01'))
        discount_type = item.get('discount_type') or 'reduce'
        discount_value = cls.to_decimal(item.get('discount_value'), 0)
        if discount_type == 'discount' and discount_value > 0:
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
        return quantity, total_price.quantize(Decimal('0.01')), subtotal_price.quantize(Decimal('0.01'))

    @classmethod
    def normalize_package_item(cls, raw, index: int):
        item_type = cls.get_raw_value(raw, 'item_type', 'itemType')
        item_id = cls.get_raw_value(raw, 'item_id', 'itemId')
        item_name = cls.get_raw_value(raw, 'item_name', 'itemName')
        if item_type not in cls.PACKAGE_ITEM_TYPE_LABELS:
            raise ServiceException(message='套餐明细项目类型不正确')
        if not item_id or not item_name:
            raise ServiceException(message='套餐明细项目不能为空')
        item = {
            'item_type': item_type,
            'item_id': cls.to_int(item_id),
            'item_name': item_name,
            'spec_id': cls.get_raw_value(raw, 'spec_id', 'specId'),
            'spec_name': cls.get_raw_value(raw, 'spec_name', 'specName'),
            'unit': cls.get_raw_value(raw, 'unit', default=''),
            'quantity': cls.get_raw_value(raw, 'quantity', default=1),
            'gift_quantity': cls.to_int(cls.get_raw_value(raw, 'gift_quantity', 'giftQuantity', default=0), 0),
            'leave_free_quantity': cls.to_int(cls.get_raw_value(raw, 'leave_free_quantity', 'leaveFreeQuantity', default=0), 0),
            'unit_price': cls.get_raw_value(raw, 'unit_price', 'unitPrice', default=0),
            'discount_type': cls.get_raw_value(raw, 'discount_type', 'discountType', default='reduce') or 'reduce',
            'discount_value': cls.to_decimal(cls.get_raw_value(raw, 'discount_value', 'discountValue', default=0), 0),
            'subtotal_price': cls.get_raw_value(raw, 'subtotal_price', 'subtotalPrice', default=None),
            'sort': cls.to_int(cls.get_raw_value(raw, 'sort', default=index), index),
        }
        quantity, total_price, subtotal_price = cls.calc_package_item_amount(item)
        item['quantity'] = quantity
        item['unit_price'] = cls.to_decimal(item['unit_price'], 0).quantize(Decimal('0.01'))
        item['total_price'] = total_price
        item['subtotal_price'] = subtotal_price
        return item

    @classmethod
    def build_package_item_payloads(cls, page_object):
        raw_items = getattr(page_object, 'items', None) or []
        if not raw_items:
            raise ServiceException(message='请至少选择一个套餐项目')
        result = []
        seen = set()
        for index, raw in enumerate(raw_items):
            item = cls.normalize_package_item(raw, index)
            key = (item['item_type'], item['item_id'], item['spec_id'])
            if key in seen:
                continue
            seen.add(key)
            item['sort'] = len(result)
            result.append(item)
        if not result:
            raise ServiceException(message='请至少选择一个套餐项目')
        return result

    @classmethod
    def calc_package_total(cls, page_object):
        items = cls.build_package_item_payloads(page_object)
        total_price = sum((item['subtotal_price'] for item in items), Decimal('0'))
        return items, total_price.quantize(Decimal('0.01'))

    @classmethod
    def build_package_do(cls, page_object, current_user_name: str):
        items, total_price = cls.calc_package_total(page_object)
        now = datetime.now()
        return (
            TeachCoursePackage(
                package_no=page_object.package_no or cls.make_package_no(),
                package_name=page_object.package_name,
                total_price=total_price,
                online_sale=page_object.online_sale or 0,
                status=page_object.status if page_object.status is not None else 1,
                create_by=current_user_name,
                create_time=now,
                update_by=current_user_name,
                update_time=now,
                remark=page_object.remark,
            ),
            items,
        )

    @classmethod
    async def save_package_items(
        cls, query_db: AsyncSession, package_id: int, item_payloads: list[dict], current_user_name: str
    ):
        await TeachCourseDao.delete_package_items_by_package_id(query_db, package_id, current_user_name)
        now = datetime.now()
        for item in item_payloads:
            await TeachCourseDao.add_package_item(
                query_db,
                TeachPackageItem(
                    package_id=package_id,
                    item_type=item['item_type'],
                    item_id=item['item_id'],
                    item_name=item['item_name'],
                    spec_id=item['spec_id'],
                    spec_name=item['spec_name'],
                    unit=item['unit'],
                    quantity=item['quantity'],
                    gift_quantity=item['gift_quantity'],
                    leave_free_quantity=item['leave_free_quantity'],
                    unit_price=item['unit_price'],
                    total_price=item['total_price'],
                    discount_type=item['discount_type'],
                    discount_value=item['discount_value'],
                    subtotal_price=item['subtotal_price'],
                    sort=item['sort'],
                    create_by=current_user_name,
                    create_time=now,
                    update_by=current_user_name,
                    update_time=now,
                ),
            )

    @classmethod
    def format_package_item_row(cls, package_item: TeachPackageItem, price_map: dict | None = None):
        item_row = CamelCaseUtil.transform_result(package_item)
        item_row['itemTypeName'] = cls.PACKAGE_ITEM_TYPE_LABELS.get(item_row.get('itemType'), item_row.get('itemType'))
        item_row['specText'] = item_row.get('specName') or '-'
        if item_row.get('itemType') == 'course':
            item_row['priceOptions'] = [
                cls.format_price_row(price) for price in (price_map or {}).get(item_row.get('itemId'), [])
            ]
        return item_row

    @classmethod
    def format_package_row(cls, package_row: dict, package_items: list[TeachPackageItem], price_map: dict | None = None):
        item_rows = [cls.format_package_item_row(item, price_map) for item in package_items]
        package_row['items'] = item_rows
        package_row['itemCount'] = len(item_rows)
        package_row['itemSummary'] = '、'.join([item.get('itemName') for item in item_rows if item.get('itemName')])
        package_row['onlineSale'] = package_row.get('onlineSale') or 0
        package_row['totalPrice'] = package_row.get('totalPrice') or Decimal('0')
        return package_row

    @classmethod
    async def attach_package_items(cls, query_db: AsyncSession, package_rows):
        package_ids = [row.get('id') for row in package_rows if row.get('id')]
        items = await TeachCourseDao.get_package_items_by_package_ids(query_db, package_ids)
        item_map = defaultdict(list)
        for item in items:
            item_map[item.package_id].append(item)
        return [cls.format_package_row(row, item_map.get(row.get('id'), [])) for row in package_rows]

    @classmethod
    async def get_teach_package_list_services(
        cls, query_db: AsyncSession, query_object: TeachCoursePackagePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        page_result = await TeachCourseDao.get_teach_package_list(query_db, query_object, data_scope_sql, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = await cls.attach_package_items(query_db, page_result.rows)
        else:
            page_result = await cls.attach_package_items(query_db, page_result)
        return page_result

    @classmethod
    async def get_teach_package_detail_services(cls, query_db: AsyncSession, package_id: int):
        package = await TeachCourseDao.get_teach_package_by_id(query_db, package_id)
        if not package:
            raise ServiceException(message='套餐不存在')
        items = await TeachCourseDao.get_package_items_by_package_id(query_db, package_id)
        course_ids = [item.item_id for item in items if item.item_type == 'course']
        prices = await TeachCourseDao.get_prices_by_course_ids(query_db, course_ids)
        price_map = defaultdict(list)
        for price in prices:
            price_map[price.course_id].append(price)
        return cls.format_package_row(CamelCaseUtil.transform_result(package), items, price_map)

    @classmethod
    async def add_teach_package_services(
        cls, query_db: AsyncSession, page_object: AddTeachCoursePackageModel, current_user_name: str
    ):
        if page_object.package_no:
            exist = await TeachCourseDao.get_teach_package_by_no(query_db, page_object.package_no)
            if exist:
                raise ServiceException(message='套餐编号已存在')
        try:
            package, items = cls.build_package_do(page_object, current_user_name)
            package = await TeachCourseDao.add_teach_package(query_db, package)
            package_id = package.id
            await cls.save_package_items(query_db, package.id, items, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': package_id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_package_services(
        cls, query_db: AsyncSession, page_object: EditTeachCoursePackageModel, current_user_name: str
    ):
        package = await TeachCourseDao.get_teach_package_by_id(query_db, page_object.id)
        if not package:
            raise ServiceException(message='套餐不存在')
        if page_object.package_no:
            exist = await TeachCourseDao.get_teach_package_by_no(query_db, page_object.package_no)
            if exist and exist.id != page_object.id:
                raise ServiceException(message='套餐编号已存在')
        items, total_price = cls.calc_package_total(page_object)
        try:
            package.package_no = page_object.package_no or package.package_no
            package.package_name = page_object.package_name
            package.total_price = total_price
            package.online_sale = page_object.online_sale or 0
            package.status = page_object.status if page_object.status is not None else 1
            package.update_by = current_user_name
            package.remark = page_object.remark
            await TeachCourseDao.edit_teach_package(query_db, package)
            await cls.save_package_items(query_db, package.id, items, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_package_services(
        cls, query_db: AsyncSession, page_object: DeleteTeachCoursePackageModel, current_user_name: str
    ):
        package_ids = [int(item) for item in page_object.package_ids.split(',') if item.strip()]
        if not package_ids:
            raise ServiceException(message='请选择要删除的套餐')
        try:
            await TeachCourseDao.delete_teach_package(query_db, package_ids, current_user_name)
            for package_id in package_ids:
                await TeachCourseDao.delete_package_items_by_package_id(query_db, package_id, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def change_package_status_services(
        cls, query_db: AsyncSession, page_object: ChangeTeachPackageStatusModel, current_user_name: str
    ):
        package = await TeachCourseDao.get_teach_package_by_id(query_db, page_object.id)
        if not package:
            raise ServiceException(message='套餐不存在')
        try:
            await TeachCourseDao.update_teach_package_status(query_db, page_object.id, page_object.status, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='状态修改成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @staticmethod
    async def export_teach_course_list_services(course_list: list):
        mapping_dict = {
            'courseName': '课程名称',
            'courseTypeName': '课程类型',
            'chargeTypeText': '收费方式',
            'priceStandard': '定价标准',
            'studentCount': '在读学员数',
            'status': '启用状态',
            'onlineSale': '线上售卖',
            'remark': '备注',
        }
        for course in course_list:
            course['status'] = '启用' if course.get('status') == 1 else '停用'
            course['onlineSale'] = '已售卖' if course.get('onlineSale') == 1 else '未售卖'
        return ExcelUtil.export_list2excel(course_list, mapping_dict)
