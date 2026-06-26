from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_card_dao import TeachCardDao
from module_teach.entity.do.teach_card_do import TeachCard, TeachCardCourse, TeachCardGrant, TeachCardLog
from module_teach.entity.vo.teach_card_vo import (
    AddTeachCardModel,
    ChangeTeachCardStatusModel,
    DeleteTeachCardModel,
    EditTeachCardModel,
    GrantTeachCardModel,
    TeachCardGrantPageQueryModel,
    TeachCardLogPageQueryModel,
    TeachCardPageQueryModel,
    VoidTeachCardGrantModel,
)
from exceptions.exception import ServiceException
from utils.common_util import CamelCaseUtil


class TeachCardService:
    """
    会员卡模块服务层
    """

    CARD_TYPE_LABELS = {
        'course': '课程卡',
        'venue_discount': '场地折扣卡',
    }
    EFFECT_TYPE_LABELS = {
        'immediate': '立即生效',
        'first_use': '首次使用后生效',
    }
    GRANT_STATUS_LABELS = {
        1: '有效',
        2: '过期',
        3: '用完',
        4: '作废',
    }
    ACTION_LABELS = {
        'grant': '发放',
        'consume': '消耗',
        'void': '作废',
        'expire': '过期',
    }

    GRANT_STATUS_VALID = 1
    GRANT_STATUS_EXPIRED = 2
    GRANT_STATUS_USED_UP = 3
    GRANT_STATUS_VOID = 4

    @classmethod
    def make_card_no(cls):
        return f'CARD{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def make_grant_no(cls):
        return f'GRANT{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def to_int(cls, value, default=0):
        if value is None or value == '':
            return default
        return int(value)

    @classmethod
    def to_decimal(cls, value, default=0):
        if value is None or value == '':
            return Decimal(str(default))
        return Decimal(str(value))

    @classmethod
    def parse_date(cls, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date()
        text = str(value).strip()
        for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d'):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    # ------------------------ 卡模板 ------------------------
    @classmethod
    def build_card_do(cls, page_object, current_user_name: str):
        now = datetime.now()
        return TeachCard(
            card_no=page_object.card_no or cls.make_card_no(),
            card_name=page_object.card_name,
            card_type=page_object.card_type or 'course',
            initial_count=cls.to_int(page_object.initial_count, 0),
            valid_days=cls.to_int(page_object.valid_days, 0),
            effect_type=page_object.effect_type or 'immediate',
            discount_rate=cls.to_decimal(page_object.discount_rate, 0),
            cover_image=page_object.cover_image,
            price=cls.to_decimal(page_object.price, 0),
            online_sale=cls.to_int(page_object.online_sale, 0),
            description=page_object.description,
            status=page_object.status if page_object.status is not None else 1,
            create_by=current_user_name,
            create_time=now,
            update_by=current_user_name,
            update_time=now,
            remark=page_object.remark,
        )

    @classmethod
    async def save_card_courses(cls, query_db: AsyncSession, card_id: int, page_object, current_user_name: str):
        await TeachCardDao.delete_courses_by_card_id(query_db, card_id, current_user_name)
        now = datetime.now()
        courses = getattr(page_object, 'courses', None) or []
        seen = set()
        for course in courses:
            course_id = cls.to_int(getattr(course, 'course_id', None) or 0, 0)
            if not course_id or course_id in seen:
                continue
            seen.add(course_id)
            await TeachCardDao.add_card_course(
                query_db,
                TeachCardCourse(
                    card_id=card_id,
                    course_id=course_id,
                    course_name=getattr(course, 'course_name', None),
                    create_by=current_user_name,
                    create_time=now,
                ),
            )

    @classmethod
    def fill_card_labels(cls, card_row: dict):
        card_row['cardTypeName'] = cls.CARD_TYPE_LABELS.get(card_row.get('cardType'), card_row.get('cardType'))
        card_row['effectTypeName'] = cls.EFFECT_TYPE_LABELS.get(card_row.get('effectType'), card_row.get('effectType'))
        return card_row

    @classmethod
    async def attach_card_courses(cls, query_db: AsyncSession, card_rows):
        card_ids = [row.get('id') for row in card_rows if row.get('id')]
        courses = await TeachCardDao.get_courses_by_card_ids(query_db, card_ids)
        course_map = defaultdict(list)
        for course in courses:
            course_map[course.card_id].append(CamelCaseUtil.transform_result(course))
        for row in card_rows:
            row['courses'] = course_map.get(row.get('id'), [])
            cls.fill_card_labels(row)
        return card_rows

    @classmethod
    async def get_teach_card_list_services(
        cls, query_db: AsyncSession, query_object: TeachCardPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        page_result = await TeachCardDao.get_teach_card_list(query_db, query_object, data_scope_sql, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = await cls.attach_card_courses(query_db, page_result.rows)
        else:
            page_result = await cls.attach_card_courses(query_db, page_result)
        return page_result

    @classmethod
    async def get_teach_card_detail_services(cls, query_db: AsyncSession, card_id: int):
        card = await TeachCardDao.get_teach_card_by_id(query_db, card_id)
        if not card:
            raise ServiceException(message='会员卡不存在')
        card_row = CamelCaseUtil.transform_result(card)
        courses = await TeachCardDao.get_courses_by_card_id(query_db, card_id)
        card_row['courses'] = [CamelCaseUtil.transform_result(course) for course in courses]
        return cls.fill_card_labels(card_row)

    @classmethod
    async def add_teach_card_services(cls, query_db: AsyncSession, page_object: AddTeachCardModel, current_user_name: str):
        if page_object.card_no:
            exist = await TeachCardDao.get_teach_card_by_no(query_db, page_object.card_no)
            if exist:
                raise ServiceException(message='卡编号已存在')
        try:
            card = await TeachCardDao.add_teach_card(query_db, cls.build_card_do(page_object, current_user_name))
            await cls.save_card_courses(query_db, card.id, page_object, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': card.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_card_services(cls, query_db: AsyncSession, page_object: EditTeachCardModel, current_user_name: str):
        card = await TeachCardDao.get_teach_card_by_id(query_db, page_object.id)
        if not card:
            raise ServiceException(message='会员卡不存在')
        if page_object.card_no:
            exist = await TeachCardDao.get_teach_card_by_no(query_db, page_object.card_no)
            if exist and exist.id != page_object.id:
                raise ServiceException(message='卡编号已存在')
        try:
            card.card_no = page_object.card_no or card.card_no
            card.card_name = page_object.card_name
            card.card_type = page_object.card_type or 'course'
            card.initial_count = cls.to_int(page_object.initial_count, 0)
            card.valid_days = cls.to_int(page_object.valid_days, 0)
            card.effect_type = page_object.effect_type or 'immediate'
            card.discount_rate = cls.to_decimal(page_object.discount_rate, 0)
            card.cover_image = page_object.cover_image
            card.price = cls.to_decimal(page_object.price, 0)
            card.online_sale = cls.to_int(page_object.online_sale, 0)
            card.description = page_object.description
            card.status = page_object.status if page_object.status is not None else 1
            card.update_by = current_user_name
            card.remark = page_object.remark
            await TeachCardDao.edit_teach_card(query_db, card)
            await cls.save_card_courses(query_db, card.id, page_object, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_card_services(cls, query_db: AsyncSession, page_object: DeleteTeachCardModel, current_user_name: str):
        card_ids = [int(item) for item in page_object.card_ids.split(',') if item.strip()]
        if not card_ids:
            raise ServiceException(message='请选择要删除的会员卡')
        try:
            await TeachCardDao.delete_teach_card(query_db, card_ids, current_user_name)
            for card_id in card_ids:
                await TeachCardDao.delete_courses_by_card_id(query_db, card_id, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def change_card_status_services(
        cls, query_db: AsyncSession, page_object: ChangeTeachCardStatusModel, current_user_name: str
    ):
        card = await TeachCardDao.get_teach_card_by_id(query_db, page_object.id)
        if not card:
            raise ServiceException(message='会员卡不存在')
        try:
            await TeachCardDao.update_teach_card_status(query_db, page_object.id, page_object.status, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='状态修改成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    # ------------------------ 发放 ------------------------
    @classmethod
    def fill_grant_labels(cls, grant_row: dict):
        grant_row['grantStatusName'] = cls.GRANT_STATUS_LABELS.get(
            grant_row.get('grantStatus'), grant_row.get('grantStatus')
        )
        return grant_row

    @classmethod
    async def grant_teach_card_services(
        cls, query_db: AsyncSession, page_object: GrantTeachCardModel, operator_id: int, operator_name: str
    ):
        card = await TeachCardDao.get_teach_card_by_id(query_db, page_object.card_id)
        if not card:
            raise ServiceException(message='会员卡不存在')
        if card.status != 1:
            raise ServiceException(message='会员卡已停用，无法发放')

        grant_count = cls.to_int(page_object.grant_count, 0) or cls.to_int(card.initial_count, 0)
        if card.card_type == 'course' and grant_count <= 0:
            raise ServiceException(message='课程卡发放次数必须大于0')

        # 计算生效/失效日期：立即生效=今天起算；首次使用后=暂不起算(留空，待首次消耗时再算)
        start_date = cls.parse_date(page_object.valid_start_date)
        if start_date is None and (card.effect_type or 'immediate') == 'immediate':
            start_date = datetime.now().date()
        end_date = None
        valid_days = cls.to_int(card.valid_days, 0)
        if start_date is not None and valid_days > 0:
            end_date = start_date + timedelta(days=valid_days)

        now = datetime.now()
        try:
            grant = await TeachCardDao.add_teach_card_grant(
                query_db,
                TeachCardGrant(
                    grant_no=cls.make_grant_no(),
                    card_id=card.id,
                    card_name=card.card_name,
                    student_id=page_object.student_id,
                    student_name=page_object.student_name,
                    grant_count=grant_count,
                    remaining_count=grant_count,
                    valid_start_date=start_date,
                    valid_end_date=end_date,
                    grant_status=cls.GRANT_STATUS_VALID,
                    operator_id=operator_id,
                    operator_name=operator_name,
                    grant_time=now,
                    create_by=operator_name,
                    create_time=now,
                    update_by=operator_name,
                    update_time=now,
                    remark=page_object.remark,
                ),
            )
            await TeachCardDao.add_teach_card_log(
                query_db,
                TeachCardLog(
                    card_id=card.id,
                    grant_id=grant.id,
                    student_id=page_object.student_id,
                    action='grant',
                    change_count=grant_count,
                    before_count=0,
                    after_count=grant_count,
                    operator_id=operator_id,
                    operator_name=operator_name,
                    create_by=operator_name,
                    create_time=now,
                    remark=page_object.remark,
                ),
            )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='发卡成功', result={'id': grant.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_teach_card_grant_list_services(
        cls, query_db: AsyncSession, query_object: TeachCardGrantPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        page_result = await TeachCardDao.get_teach_card_grant_list(query_db, query_object, data_scope_sql, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = [cls.fill_grant_labels(row) for row in page_result.rows]
        else:
            page_result = [cls.fill_grant_labels(row) for row in page_result]
        return page_result

    @classmethod
    async def void_teach_card_grant_services(
        cls, query_db: AsyncSession, page_object: VoidTeachCardGrantModel, operator_id: int, operator_name: str
    ):
        grant = await TeachCardDao.get_teach_card_grant_by_id(query_db, page_object.id)
        if not grant:
            raise ServiceException(message='发放记录不存在')
        if grant.grant_status == cls.GRANT_STATUS_VOID:
            raise ServiceException(message='该发放记录已作废')
        now = datetime.now()
        before_count = cls.to_int(grant.remaining_count, 0)
        try:
            grant.grant_status = cls.GRANT_STATUS_VOID
            grant.remaining_count = 0
            grant.update_by = operator_name
            grant.remark = page_object.remark or grant.remark
            await TeachCardDao.edit_teach_card_grant(query_db, grant)
            await TeachCardDao.add_teach_card_log(
                query_db,
                TeachCardLog(
                    card_id=grant.card_id,
                    grant_id=grant.id,
                    student_id=grant.student_id,
                    action='void',
                    change_count=before_count,
                    before_count=before_count,
                    after_count=0,
                    operator_id=operator_id,
                    operator_name=operator_name,
                    create_by=operator_name,
                    create_time=now,
                    remark=page_object.remark,
                ),
            )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='作废成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_student_cards_services(cls, query_db: AsyncSession, student_id: int):
        grants = await TeachCardDao.get_grants_by_student_id(query_db, student_id)
        rows = CamelCaseUtil.transform_result(grants)
        rows = rows if isinstance(rows, list) else [rows]
        return [cls.fill_grant_labels(row) for row in rows]

    # ------------------------ 操作记录 ------------------------
    @classmethod
    async def get_teach_card_log_list_services(
        cls, query_db: AsyncSession, query_object: TeachCardLogPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        page_result = await TeachCardDao.get_teach_card_log_list(query_db, query_object, data_scope_sql, is_page)
        rows = page_result.rows if hasattr(page_result, 'rows') else page_result
        for row in rows:
            row['actionName'] = cls.ACTION_LABELS.get(row.get('action'), row.get('action'))
        return page_result
