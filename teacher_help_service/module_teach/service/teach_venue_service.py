import re
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from config.env import BusinessRuleConfig
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_venue_dao import TeachVenueDao
from module_teach.service.teach_card_service import TeachCardService
from module_teach.entity.do.teach_venue_do import (
    TeachCourt,
    TeachCourtBooking,
    TeachCourtPriceRule,
    TeachCourtTime,
    TeachVenue,
)
from module_teach.entity.vo.teach_venue_vo import (
    AddTeachBookingModel,
    AddTeachCourtModel,
    AddTeachVenueModel,
    CancelBookingModel,
    CancelLockGroupModel,
    ChangeTeachVenueStatusModel,
    DeleteTeachCourtModel,
    DeleteTeachVenueModel,
    EditTeachCourtModel,
    EditTeachVenueModel,
    LockCourtBookingModel,
    TeachBookingGridQueryModel,
    TeachBookingPageQueryModel,
    TeachBookingQuoteQueryModel,
    TeachVenuePageQueryModel,
    VerifyBookingModel,
)
from exceptions.exception import ServiceException
from utils.common_util import CamelCaseUtil


class TeachVenueService:
    """
    场地管理模块服务层
    """

    BOOKING_TYPE_LABELS = {'normal': '预订', 'lock': '锁场'}
    ORIGIN_LABELS = {'admin': '代预订', 'online': '线上'}
    PAY_STATUS_LABELS = {0: '未付', 1: '已付', 2: '已退'}
    BOOKING_STATUS_LABELS = {1: '已预订', 2: '已核销', 3: '已取消'}

    @classmethod
    def make_venue_no(cls):
        return f'VENUE{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def make_court_no(cls):
        return f'COURT{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def make_booking_no(cls):
        return f'BK{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    def to_decimal(cls, value, default=0):
        if value is None or value == '':
            return Decimal(str(default))
        return Decimal(str(value))

    @classmethod
    def parse_date(cls, value):
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if not value:
            raise ServiceException(message='预订日期不能为空')
        try:
            return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
        except ValueError:
            raise ServiceException(message='预订日期格式不正确(应为YYYY-MM-DD)')

    TIME_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$')

    @classmethod
    def normalize_time(cls, value, field_name: str = '时间'):
        """
        把时间统一为补零的 HH:MM 字符串（如 9:00 -> 09:00），保证字符串字典序与时间先后一致
        允许 24:00 作为一天的结束时间
        """
        if isinstance(value, time):
            return value.strftime('%H:%M')
        if value is None or str(value).strip() == '':
            raise ServiceException(message=f'{field_name}不能为空')
        match = cls.TIME_PATTERN.match(str(value).strip())
        if not match:
            raise ServiceException(message=f'{field_name}格式不正确(应为HH:MM)')
        hour, minute = int(match.group(1)), int(match.group(2))
        second = int(match.group(3) or 0)
        if (hour == 24 and minute == 0 and second == 0) or (0 <= hour <= 23 and 0 <= minute <= 59 and second <= 59):
            return f'{hour:02d}:{minute:02d}'
        raise ServiceException(message=f'{field_name}超出范围(00:00-24:00)')

    @classmethod
    def validate_time_range(cls, start_time: str, end_time: str):
        """
        校验并返回规范化后的 (start_time, end_time)
        """
        if not start_time or not end_time:
            raise ServiceException(message='开始时间和结束时间不能为空')
        start_time = cls.normalize_time(start_time, '开始时间')
        end_time = cls.normalize_time(end_time, '结束时间')
        if start_time == '24:00':
            raise ServiceException(message='开始时间不能为24:00')
        if start_time >= end_time:
            raise ServiceException(message='结束时间必须晚于开始时间')
        return start_time, end_time

    @classmethod
    def time_to_minutes(cls, value: str):
        hour, minute = value.split(':')
        return int(hour) * 60 + int(minute)

    @classmethod
    def safe_normalize_time(cls, value):
        """读取存量数据时使用：无法解析时原样返回，避免历史脏数据导致整页报错"""
        try:
            return cls.normalize_time(value)
        except ServiceException:
            return value

    @classmethod
    def segment_price(cls, half_price, hour_price, minutes: int):
        """
        一段时长按给定价格计费：有半小时价时按半小时折算，否则按小时价按分钟折算
        """
        half_price = cls.to_decimal(half_price, 0)
        hour_price = cls.to_decimal(hour_price, 0)
        if half_price > 0:
            return half_price * Decimal(minutes) / Decimal(30)
        if hour_price > 0:
            return hour_price * Decimal(minutes) / Decimal(60)
        return Decimal('0')

    @classmethod
    def split_by_price_rules(cls, court: TeachCourt, start_time: str, end_time: str, rules=None):
        """
        把 [start_time, end_time) 按分时价格规则切段，返回 [(开始分钟, 结束分钟, 半小时价, 小时价, 规则ID或None)]
        规则未覆盖的部分使用场地默认价格；规则之间不允许重叠（保存时校验）
        """
        start = cls.time_to_minutes(start_time)
        end = cls.time_to_minutes(end_time)
        windows = []
        for rule in rules or []:
            rule_start = cls.time_to_minutes(cls.safe_normalize_time(rule.start_time))
            rule_end = cls.time_to_minutes(cls.safe_normalize_time(rule.end_time))
            overlap_start, overlap_end = max(start, rule_start), min(end, rule_end)
            if overlap_start < overlap_end:
                windows.append((overlap_start, overlap_end, rule))
        windows.sort(key=lambda item: item[0])
        segments = []
        cursor = start
        for overlap_start, overlap_end, rule in windows:
            if overlap_start < cursor:
                overlap_start = cursor
            if overlap_start >= overlap_end:
                continue
            if cursor < overlap_start:
                segments.append((cursor, overlap_start, court.price_per_half_hour, court.price_per_hour, None))
            segments.append((overlap_start, overlap_end, rule.price_per_half_hour, rule.price_per_hour, rule.id))
            cursor = overlap_end
        if cursor < end:
            segments.append((cursor, end, court.price_per_half_hour, court.price_per_hour, None))
        return segments

    @classmethod
    def calc_booking_amount(cls, court: TeachCourt, start_time: str, end_time: str, rules=None):
        """
        按场地价格由后端计算应收金额（不信任前端传入金额）：
        1. 按当天星期的分时价格规则切段，规则未覆盖的部分用场地默认价格；
        2. 每段有半小时价时按半小时折算，否则按小时价按分钟折算，均未配置时该段为 0；
        3. 若最后一段按半小时计价，总时长不足半小时整数倍的部分按最后一段的半小时价补足（向上取整到半小时）。
        没有分时规则时结果与 P1 一致：有半小时价按半小时向上取整，否则按小时价按分钟折算
        """
        segments = cls.split_by_price_rules(court, start_time, end_time, rules)
        amount = Decimal('0')
        for seg_start, seg_end, half_price, hour_price, _ in segments:
            amount += cls.segment_price(half_price, hour_price, seg_end - seg_start)
        if segments:
            minutes = segments[-1][1] - segments[0][0]
            last_half_price = cls.to_decimal(segments[-1][2], 0)
            remainder = minutes % 30
            if last_half_price > 0 and remainder:
                amount += last_half_price * Decimal(30 - remainder) / Decimal(30)
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @classmethod
    async def get_day_price_rules(cls, query_db: AsyncSession, court_id: int, booking_date: date):
        return list(await TeachVenueDao.get_price_rules_by_court_ids(query_db, [court_id], booking_date.isoweekday()))

    @classmethod
    async def calc_court_amount(
        cls, query_db: AsyncSession, court: TeachCourt, booking_date: date, start_time, end_time
    ):
        rules = await cls.get_day_price_rules(query_db, court.id, booking_date)
        return cls.calc_booking_amount(court, start_time, end_time, rules)

    @classmethod
    async def assert_within_open_time(cls, query_db: AsyncSession, court_id: int, booking_date: date, start, end):
        """
        VENUE_BOOKING_REQUIRE_OPEN_TIME=true 时，预订/锁场必须完全落在当天某个可约时段内（默认不校验）
        """
        if not BusinessRuleConfig.venue_booking_require_open_time:
            return
        week_day = booking_date.isoweekday()
        for t in await TeachVenueDao.get_times_by_court_id(query_db, court_id):
            if t.week_day != week_day:
                continue
            if cls.safe_normalize_time(t.start_time) <= start and cls.safe_normalize_time(t.end_time) >= end:
                return
        raise ServiceException(message='所选时间不在场地可约时段内')

    @classmethod
    async def lock_bookable_court(cls, query_db: AsyncSession, court_id: int):
        """
        加锁读取场地并校验场地、场馆均为启用状态
        同一场地的预订/锁场在场地行锁上串行，配合冲突查询防止并发撞场
        """
        court = await TeachVenueDao.get_court_by_id(query_db, court_id, for_update=True)
        if not court:
            raise ServiceException(message='场地不存在')
        if court.status != 1:
            raise ServiceException(message='场地已停用，无法预订')
        venue = await TeachVenueDao.get_venue_by_id(query_db, court.venue_id)
        if not venue or venue.status != 1:
            raise ServiceException(message='所属场馆不存在或已停用，无法预订')
        return court

    # ======================== 场馆 ========================
    @classmethod
    async def get_venue_list_services(
        cls, query_db: AsyncSession, query_object: TeachVenuePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        return await TeachVenueDao.get_venue_list(query_db, query_object, data_scope_sql, is_page)

    @classmethod
    async def get_venue_detail_services(cls, query_db: AsyncSession, venue_id: int):
        venue = await TeachVenueDao.get_venue_by_id(query_db, venue_id)
        if not venue:
            raise ServiceException(message='场馆不存在')
        return CamelCaseUtil.transform_result(venue)

    @classmethod
    async def add_venue_services(cls, query_db: AsyncSession, page_object: AddTeachVenueModel, current_user_name: str):
        if page_object.venue_no:
            exist = await TeachVenueDao.get_venue_by_no(query_db, page_object.venue_no)
            if exist:
                raise ServiceException(message='场馆编号已存在')
        now = datetime.now()
        try:
            venue = TeachVenue(
                venue_no=page_object.venue_no or cls.make_venue_no(),
                venue_name=page_object.venue_name,
                address=page_object.address,
                description=page_object.description,
                status=page_object.status if page_object.status is not None else 1,
                create_by=current_user_name,
                create_time=now,
                update_by=current_user_name,
                update_time=now,
                remark=page_object.remark,
            )
            venue = await TeachVenueDao.add_venue(query_db, venue)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': venue.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_venue_services(cls, query_db: AsyncSession, page_object: EditTeachVenueModel, current_user_name: str):
        venue = await TeachVenueDao.get_venue_by_id(query_db, page_object.id)
        if not venue:
            raise ServiceException(message='场馆不存在')
        if page_object.venue_no:
            exist = await TeachVenueDao.get_venue_by_no(query_db, page_object.venue_no)
            if exist and exist.id != page_object.id:
                raise ServiceException(message='场馆编号已存在')
        try:
            venue.venue_no = page_object.venue_no or venue.venue_no
            venue.venue_name = page_object.venue_name
            venue.address = page_object.address
            venue.description = page_object.description
            venue.status = page_object.status if page_object.status is not None else 1
            venue.update_by = current_user_name
            venue.remark = page_object.remark
            await TeachVenueDao.edit_venue(query_db, venue)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def change_venue_status_services(
        cls, query_db: AsyncSession, page_object: ChangeTeachVenueStatusModel, current_user_name: str
    ):
        venue = await TeachVenueDao.get_venue_by_id(query_db, page_object.id)
        if not venue:
            raise ServiceException(message='场馆不存在')
        try:
            await TeachVenueDao.update_venue_status(query_db, page_object.id, page_object.status, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='状态修改成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_venue_services(
        cls, query_db: AsyncSession, page_object: DeleteTeachVenueModel, current_user_name: str
    ):
        venue_ids = [int(item) for item in page_object.venue_ids.split(',') if item.strip()]
        if not venue_ids:
            raise ServiceException(message='请选择要删除的场馆')
        try:
            for venue_id in venue_ids:
                courts = await TeachVenueDao.get_courts_by_venue_id(query_db, venue_id)
                if courts:
                    raise ServiceException(message='该场馆下存在场地，请先删除场地')
            await TeachVenueDao.delete_venue(query_db, venue_ids, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    # ======================== 场地 ========================
    @classmethod
    async def get_court_list_services(cls, query_db: AsyncSession, venue_id: int | None = None, **filters):
        courts = await TeachVenueDao.get_court_list(query_db, venue_id, **filters)
        court_ids = [court.id for court in courts]
        times = await TeachVenueDao.get_times_by_court_ids(query_db, court_ids)
        time_map: dict[int, list] = {}
        for t in times:
            time_map.setdefault(t.court_id, []).append(CamelCaseUtil.transform_result(t))
        rule_map: dict[int, list] = {}
        for rule in await TeachVenueDao.get_price_rules_by_court_ids(query_db, court_ids):
            rule_map.setdefault(rule.court_id, []).append(CamelCaseUtil.transform_result(rule))
        rows = []
        for court in courts:
            row = CamelCaseUtil.transform_result(court)
            row['times'] = time_map.get(court.id, [])
            row['priceRules'] = rule_map.get(court.id, [])
            rows.append(row)
        return rows

    @classmethod
    async def get_court_detail_services(cls, query_db: AsyncSession, court_id: int):
        court = await TeachVenueDao.get_court_by_id(query_db, court_id)
        if not court:
            raise ServiceException(message='场地不存在')
        times = await TeachVenueDao.get_times_by_court_id(query_db, court_id)
        rules = await TeachVenueDao.get_price_rules_by_court_ids(query_db, [court_id])
        row = CamelCaseUtil.transform_result(court)
        row['times'] = [CamelCaseUtil.transform_result(t) for t in times]
        row['priceRules'] = [CamelCaseUtil.transform_result(rule) for rule in rules]
        return row

    @classmethod
    async def save_court_times(cls, query_db: AsyncSession, court_id: int, times, current_user_name: str):
        await TeachVenueDao.delete_times_by_court_id(query_db, court_id)
        now = datetime.now()
        for t in times or []:
            week_day = getattr(t, 'week_day', None)
            start_time = getattr(t, 'start_time', None)
            end_time = getattr(t, 'end_time', None)
            if week_day is None or not start_time or not end_time:
                continue
            start_time, end_time = cls.validate_time_range(start_time, end_time)
            await TeachVenueDao.add_court_time(
                query_db,
                TeachCourtTime(
                    court_id=court_id,
                    week_day=int(week_day),
                    start_time=start_time,
                    end_time=end_time,
                    create_by=current_user_name,
                    create_time=now,
                ),
            )

    @classmethod
    async def save_court_price_rules(cls, query_db: AsyncSession, court_id: int, rules, current_user_name: str):
        """
        保存分时价格规则（整体替换）：星期 1-7、时间合法、价格不为负、同一星期内时段不重叠
        rules 为 None 时不做任何修改
        """
        if rules is None:
            return
        normalized = []
        for rule in rules:
            week_day = int(rule.week_day) if rule.week_day is not None else 0
            if week_day < 1 or week_day > 7:
                raise ServiceException(message='价格规则的星期必须为1-7')
            start_time, end_time = cls.validate_time_range(rule.start_time, rule.end_time)
            half_price = cls.to_decimal(rule.price_per_half_hour, 0)
            hour_price = cls.to_decimal(rule.price_per_hour, 0)
            if half_price < 0 or hour_price < 0:
                raise ServiceException(message='价格规则的价格不能小于0')
            normalized.append((week_day, start_time, end_time, hour_price, half_price))
        normalized.sort()
        for prev, cur in zip(normalized, normalized[1:]):
            if prev[0] == cur[0] and cur[1] < prev[2]:
                raise ServiceException(
                    message=f'星期{cur[0]}的价格规则时段重叠：{prev[1]}-{prev[2]} 与 {cur[1]}-{cur[2]}'
                )
        await TeachVenueDao.delete_price_rules_by_court_id(query_db, court_id)
        now = datetime.now()
        for week_day, start_time, end_time, hour_price, half_price in normalized:
            await TeachVenueDao.add_price_rule(
                query_db,
                TeachCourtPriceRule(
                    court_id=court_id,
                    week_day=week_day,
                    start_time=start_time,
                    end_time=end_time,
                    price_per_hour=hour_price,
                    price_per_half_hour=half_price,
                    create_by=current_user_name,
                    create_time=now,
                ),
            )

    @classmethod
    async def add_court_services(cls, query_db: AsyncSession, page_object: AddTeachCourtModel, current_user_name: str):
        venue = await TeachVenueDao.get_venue_by_id(query_db, page_object.venue_id)
        if not venue:
            raise ServiceException(message='所属场馆不存在')
        now = datetime.now()
        try:
            court = TeachCourt(
                venue_id=page_object.venue_id,
                venue_name=venue.venue_name,
                court_no=page_object.court_no or cls.make_court_no(),
                court_name=page_object.court_name,
                court_type=page_object.court_type,
                price_per_hour=cls.to_decimal(page_object.price_per_hour, 0),
                price_per_half_hour=cls.to_decimal(page_object.price_per_half_hour, 0),
                status=page_object.status if page_object.status is not None else 1,
                create_by=current_user_name,
                create_time=now,
                update_by=current_user_name,
                update_time=now,
                remark=page_object.remark,
            )
            court = await TeachVenueDao.add_court(query_db, court)
            await cls.save_court_times(query_db, court.id, page_object.times, current_user_name)
            await cls.save_court_price_rules(query_db, court.id, page_object.price_rules, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功', result={'id': court.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_court_services(cls, query_db: AsyncSession, page_object: EditTeachCourtModel, current_user_name: str):
        court = await TeachVenueDao.get_court_by_id(query_db, page_object.id)
        if not court:
            raise ServiceException(message='场地不存在')
        venue = await TeachVenueDao.get_venue_by_id(query_db, page_object.venue_id)
        if not venue:
            raise ServiceException(message='所属场馆不存在')
        try:
            court.venue_id = page_object.venue_id
            court.venue_name = venue.venue_name
            court.court_no = page_object.court_no or court.court_no
            court.court_name = page_object.court_name
            court.court_type = page_object.court_type
            court.price_per_hour = cls.to_decimal(page_object.price_per_hour, 0)
            court.price_per_half_hour = cls.to_decimal(page_object.price_per_half_hour, 0)
            court.status = page_object.status if page_object.status is not None else 1
            court.update_by = current_user_name
            court.remark = page_object.remark
            await TeachVenueDao.edit_court(query_db, court)
            await cls.save_court_times(query_db, court.id, page_object.times, current_user_name)
            await cls.save_court_price_rules(query_db, court.id, page_object.price_rules, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_court_services(
        cls, query_db: AsyncSession, page_object: DeleteTeachCourtModel, current_user_name: str
    ):
        court_ids = [int(item) for item in page_object.court_ids.split(',') if item.strip()]
        if not court_ids:
            raise ServiceException(message='请选择要删除的场地')
        try:
            await TeachVenueDao.delete_court(query_db, court_ids, current_user_name)
            for court_id in court_ids:
                await TeachVenueDao.delete_times_by_court_id(query_db, court_id)
                await TeachVenueDao.delete_price_rules_by_court_id(query_db, court_id)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    # ======================== 订场 / 预订 ========================
    @classmethod
    async def assert_no_conflict(cls, query_db: AsyncSession, court_id: int, booking_date, start_time, end_time):
        """同场地同日同时间段冲突校验：存在重叠的有效预订(已预订/已核销)即冲突"""
        conflicts = await TeachVenueDao.get_conflict_bookings(query_db, court_id, booking_date, start_time, end_time)
        if conflicts:
            raise ServiceException(message='该场地在所选时间段已被预订，请重新选择')

    @classmethod
    async def get_booking_grid_services(cls, query_db: AsyncSession, query_object: TeachBookingGridQueryModel):
        venue = await TeachVenueDao.get_venue_by_id(query_db, query_object.venue_id)
        if not venue:
            raise ServiceException(message='场馆不存在')
        booking_date = cls.parse_date(query_object.date)
        week_day = booking_date.isoweekday()  # 1-7
        courts = await TeachVenueDao.get_courts_by_venue_id(query_db, query_object.venue_id)
        court_ids = [court.id for court in courts]
        times = await TeachVenueDao.get_times_by_court_ids(query_db, court_ids)
        bookings = await TeachVenueDao.get_bookings_by_date(query_db, court_ids, booking_date)
        day_rule_map: dict[int, list] = {}
        for rule in await TeachVenueDao.get_price_rules_by_court_ids(query_db, court_ids, week_day):
            day_rule_map.setdefault(rule.court_id, []).append(rule)

        time_map: dict[int, list] = {}
        for t in times:
            if t.week_day == week_day:
                time_map.setdefault(t.court_id, []).append(
                    (cls.safe_normalize_time(t.start_time), cls.safe_normalize_time(t.end_time))
                )
        booking_map: dict[int, list] = {}
        for b in bookings:
            booking_map.setdefault(b.court_id, []).append(
                (cls.safe_normalize_time(b.start_time), cls.safe_normalize_time(b.end_time), b)
            )

        grid = []
        for court in courts:
            slots = []
            for slot_start, slot_end in sorted(time_map.get(court.id, [])):
                occupied = None
                for booking_start, booking_end, b in booking_map.get(court.id, []):
                    if booking_start < slot_end and booking_end > slot_start:
                        occupied = b
                        break
                slots.append(
                    {
                        'startTime': slot_start,
                        'endTime': slot_end,
                        'status': 'occupied' if occupied else 'available',
                        'bookingId': occupied.id if occupied else None,
                        'bookingType': occupied.booking_type if occupied else None,
                        'customerName': occupied.customer_name if occupied else None,
                        'lockGroupNo': occupied.lock_group_no if occupied else None,
                        'pricePerHour': court.price_per_hour,
                        'pricePerHalfHour': court.price_per_half_hour,
                        'amount': cls.calc_booking_amount(
                            court, slot_start, slot_end, day_rule_map.get(court.id, [])
                        ) if slot_start < slot_end else Decimal('0'),
                    }
                )
            grid.append(
                {
                    'courtId': court.id,
                    'courtName': court.court_name,
                    'courtType': court.court_type,
                    'pricePerHour': court.price_per_hour,
                    'pricePerHalfHour': court.price_per_half_hour,
                    'priceRules': [CamelCaseUtil.transform_result(rule) for rule in day_rule_map.get(court.id, [])],
                    'slots': slots,
                }
            )
        return {'date': booking_date.strftime('%Y-%m-%d'), 'weekDay': week_day, 'venueId': venue.id, 'courts': grid}

    @classmethod
    async def add_booking_services(
        cls, query_db: AsyncSession, page_object: AddTeachBookingModel, operator_id, operator_name: str
    ):
        booking_date = cls.parse_date(page_object.booking_date)
        start_time, end_time = cls.validate_time_range(page_object.start_time, page_object.end_time)
        try:
            court = await cls.lock_bookable_court(query_db, page_object.court_id)
            await cls.assert_within_open_time(query_db, court.id, booking_date, start_time, end_time)
            await cls.assert_no_conflict(query_db, court.id, booking_date, start_time, end_time)
            now = datetime.now()
            booking_type = page_object.booking_type or 'normal'
            if booking_type != 'normal':
                raise ServiceException(message='锁场请使用锁场功能')
            amount = await cls.calc_court_amount(query_db, court, booking_date, start_time, end_time)
            discount_amount = cls.to_decimal(page_object.discount_amount, 0)
            if discount_amount < 0 or discount_amount > amount:
                raise ServiceException(message='减免金额不能小于0且不能超过应收金额')
            card_grant = card = None
            if page_object.card_grant_id:
                # 场地折扣卡：校验归属/状态/有效期（发放行加锁），按折后价计算优惠，订单创建后记录使用日志
                if not page_object.customer_id:
                    raise ServiceException(message='使用会员卡时必须选择学员')
                card_grant, card = await TeachCardService.lock_usable_grant(
                    query_db, page_object.card_grant_id, page_object.customer_id, 'venue_discount'
                )
                pay_ratio = TeachCardService.resolve_pay_ratio(card.discount_rate)
                card_discount = ((amount - discount_amount) * (Decimal('1') - pay_ratio)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                discount_amount += card_discount
            booking = TeachCourtBooking(
                booking_no=cls.make_booking_no(),
                court_id=court.id,
                court_name=court.court_name,
                venue_id=court.venue_id,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                customer_id=page_object.customer_id,
                customer_name=page_object.customer_name,
                customer_phone=page_object.customer_phone,
                booking_type=booking_type,
                origin=page_object.origin or 'admin',
                amount=amount,
                discount_amount=discount_amount,
                card_grant_id=page_object.card_grant_id,
                pay_status=page_object.pay_status if page_object.pay_status is not None else 0,
                booking_status=1,
                operator_id=operator_id,
                operator_name=operator_name,
                create_by=operator_name,
                create_time=now,
                update_by=operator_name,
                update_time=now,
                remark=page_object.remark,
            )
            booking = await TeachVenueDao.add_booking(query_db, booking)
            if card_grant:
                await TeachCardService.consume_grant_in_transaction(
                    query_db, card_grant, card, 0, operator_id, operator_name, f'订场使用：{booking.booking_no}'
                )
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message='预订成功',
                result={
                    'id': booking.id,
                    'bookingNo': booking.booking_no,
                    'amount': booking.amount,
                    'discountAmount': booking.discount_amount,
                },
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    def expand_lock_dates(cls, page_object: LockCourtBookingModel):
        """
        锁场日期展开：只传 booking_date 为单日；传 end_date 时为日期范围（含首尾），可按 week_days 过滤星期
        """
        start_date = cls.parse_date(page_object.booking_date)
        if not page_object.end_date:
            if page_object.week_days and start_date.isoweekday() not in page_object.week_days:
                raise ServiceException(message='所选日期不在指定星期内')
            return [start_date]
        end_date = cls.parse_date(page_object.end_date)
        if end_date < start_date:
            raise ServiceException(message='锁场结束日期不能早于开始日期')
        if (end_date - start_date).days > 366:
            raise ServiceException(message='锁场日期范围不能超过一年')
        week_days = set(page_object.week_days or [])
        if any(day < 1 or day > 7 for day in week_days):
            raise ServiceException(message='星期必须为1-7')
        dates = []
        current = start_date
        while current <= end_date:
            if not week_days or current.isoweekday() in week_days:
                dates.append(current)
            current += timedelta(days=1)
        if not dates:
            raise ServiceException(message='所选日期范围内没有符合星期条件的日期')
        return dates

    @classmethod
    async def lock_court_services(
        cls, query_db: AsyncSession, page_object: LockCourtBookingModel, operator_id, operator_name: str
    ):
        """
        锁场：支持单日单场地，也支持“日期范围 x 星期 x 多场地”批量锁场
        批量锁场全部成功或全部失败；同一批次共用 lock_group_no，可按批次解除
        """
        start_time, end_time = cls.validate_time_range(page_object.start_time, page_object.end_time)
        dates = cls.expand_lock_dates(page_object)
        court_ids = sorted({int(item) for item in (page_object.court_ids or [page_object.court_id]) if item})
        if not court_ids:
            raise ServiceException(message='请选择锁场场地')
        total = len(dates) * len(court_ids)
        if total > BusinessRuleConfig.venue_lock_batch_max:
            raise ServiceException(
                message=f'单次最多锁场{BusinessRuleConfig.venue_lock_batch_max}条，当前为{total}条，请缩小范围'
            )
        is_batch = total > 1 or bool(page_object.end_date) or bool(page_object.court_ids)
        lock_group_no = cls.make_lock_group_no() if is_batch else None
        try:
            conflicts = []
            courts = []
            # 按场地ID顺序加行锁，避免多个批量锁场互相等待
            for court_id in court_ids:
                courts.append(await cls.lock_bookable_court(query_db, court_id))
            for court in courts:
                for booking_date in dates:
                    await cls.assert_within_open_time(query_db, court.id, booking_date, start_time, end_time)
                    exists = await TeachVenueDao.get_conflict_bookings(
                        query_db, court.id, booking_date, start_time, end_time
                    )
                    if exists:
                        conflicts.append(f'{court.court_name} {booking_date.strftime("%Y-%m-%d")}')
            if conflicts:
                preview = '、'.join(conflicts[:10]) + (f' 等{len(conflicts)}处' if len(conflicts) > 10 else '')
                raise ServiceException(message=f'以下场地时段已被预订或锁定，未锁场：{preview}')
            now = datetime.now()
            booking_ids = []
            for court in courts:
                for booking_date in dates:
                    booking = TeachCourtBooking(
                        booking_no=cls.make_booking_no(),
                        court_id=court.id,
                        court_name=court.court_name,
                        venue_id=court.venue_id,
                        booking_date=booking_date,
                        start_time=start_time,
                        end_time=end_time,
                        booking_type='lock',
                        lock_group_no=lock_group_no,
                        origin='admin',
                        amount=Decimal('0'),
                        discount_amount=Decimal('0'),
                        pay_status=0,
                        booking_status=1,
                        cancel_reason=page_object.cancel_reason,
                        operator_id=operator_id,
                        operator_name=operator_name,
                        create_by=operator_name,
                        create_time=now,
                        update_by=operator_name,
                        update_time=now,
                        remark=page_object.remark,
                    )
                    booking = await TeachVenueDao.add_booking(query_db, booking)
                    booking_ids.append(booking.id)
            await query_db.commit()
            result = {'id': booking_ids[0], 'count': len(booking_ids), 'lockGroupNo': lock_group_no}
            return CrudResponseModel(is_success=True, message=f'锁场成功，共{len(booking_ids)}条', result=result)
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    def make_lock_group_no(cls):
        return f'LK{datetime.now().strftime("%Y%m%d%H%M%S%f")}{uuid4().hex[:4].upper()}'

    @classmethod
    async def cancel_lock_group_services(
        cls, query_db: AsyncSession, page_object: CancelLockGroupModel, operator_name: str
    ):
        """
        按批次解除锁场：把批次中仍为“已预订”的锁场记录置为已取消（可只解除某日期之后的）
        """
        if not page_object.lock_group_no:
            raise ServiceException(message='锁场批次号不能为空')
        from_date = cls.parse_date(page_object.from_date) if page_object.from_date else None
        try:
            bookings = await TeachVenueDao.get_lock_group_bookings(query_db, page_object.lock_group_no, from_date)
            if not bookings:
                raise ServiceException(message='该批次没有可解除的锁场记录')
            for booking in bookings:
                booking.booking_status = 3
                booking.cancel_reason = page_object.cancel_reason or '解除锁场'
                booking.update_by = operator_name
                booking.update_time = datetime.now()
            await query_db.flush()
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message=f'已解除{len(bookings)}条锁场', result={'count': len(bookings)}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_booking_quote_services(cls, query_db: AsyncSession, query_object: TeachBookingQuoteQueryModel):
        """
        预订报价（只读）：返回后端计算的应收金额与分段明细，供代预订弹窗展示
        """
        booking_date = cls.parse_date(query_object.booking_date)
        start_time, end_time = cls.validate_time_range(query_object.start_time, query_object.end_time)
        court = await TeachVenueDao.get_court_by_id(query_db, query_object.court_id)
        if not court:
            raise ServiceException(message='场地不存在')
        rules = await cls.get_day_price_rules(query_db, court.id, booking_date)
        segments = [
            {
                'startTime': f'{seg_start // 60:02d}:{seg_start % 60:02d}',
                'endTime': f'{seg_end // 60:02d}:{seg_end % 60:02d}',
                'pricePerHalfHour': cls.to_decimal(half_price, 0),
                'pricePerHour': cls.to_decimal(hour_price, 0),
                'priceRuleId': rule_id,
            }
            for seg_start, seg_end, half_price, hour_price, rule_id in cls.split_by_price_rules(
                court, start_time, end_time, rules
            )
        ]
        conflicts = await TeachVenueDao.get_conflict_bookings(query_db, court.id, booking_date, start_time, end_time)
        return {
            'courtId': court.id,
            'bookingDate': booking_date.strftime('%Y-%m-%d'),
            'startTime': start_time,
            'endTime': end_time,
            'amount': cls.calc_booking_amount(court, start_time, end_time, rules),
            'segments': segments,
            'available': not conflicts,
        }

    @classmethod
    async def get_booking_list_services(
        cls, query_db: AsyncSession, query_object: TeachBookingPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        page_result = await TeachVenueDao.get_booking_list(query_db, query_object, data_scope_sql, is_page)
        if hasattr(page_result, 'rows'):
            page_result.rows = [cls.fill_booking_labels(row) for row in page_result.rows]
        else:
            page_result = [cls.fill_booking_labels(row) for row in page_result]
        return page_result

    @classmethod
    def fill_booking_labels(cls, row: dict):
        row['bookingTypeName'] = cls.BOOKING_TYPE_LABELS.get(row.get('bookingType'), row.get('bookingType'))
        row['originName'] = cls.ORIGIN_LABELS.get(row.get('origin'), row.get('origin'))
        row['payStatusName'] = cls.PAY_STATUS_LABELS.get(row.get('payStatus'))
        row['bookingStatusName'] = cls.BOOKING_STATUS_LABELS.get(row.get('bookingStatus'))
        return row

    @classmethod
    async def get_booking_detail_services(cls, query_db: AsyncSession, booking_id: int):
        booking = await TeachVenueDao.get_booking_by_id(query_db, booking_id)
        if not booking:
            raise ServiceException(message='预订单不存在')
        return cls.fill_booking_labels(CamelCaseUtil.transform_result(booking))

    @classmethod
    async def verify_booking_services(
        cls, query_db: AsyncSession, page_object: VerifyBookingModel, operator_name: str
    ):
        try:
            booking = await TeachVenueDao.get_booking_by_id(query_db, page_object.id, for_update=True)
            if not booking:
                raise ServiceException(message='预订单不存在')
            if booking.booking_type == 'lock':
                raise ServiceException(message='锁场记录无需核销')
            if booking.booking_status == 2:
                raise ServiceException(message='该预订单已核销')
            if booking.booking_status == 3:
                raise ServiceException(message='该预订单已取消，无法核销')
            booking.booking_status = 2
            booking.verify_time = datetime.now()
            booking.update_by = operator_name
            await TeachVenueDao.edit_booking(query_db, booking)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='核销成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def cancel_booking_services(
        cls, query_db: AsyncSession, page_object: CancelBookingModel, operator_name: str
    ):
        try:
            booking = await TeachVenueDao.get_booking_by_id(query_db, page_object.id, for_update=True)
            if not booking:
                raise ServiceException(message='预订单不存在')
            if booking.booking_status == 3:
                raise ServiceException(message='该预订单已取消')
            if booking.booking_status == 2:
                raise ServiceException(message='该预订单已核销，不能取消')
            refund_amount = cls.to_decimal(page_object.refund_amount, 0)
            paid_amount = cls.to_decimal(booking.amount, 0) - cls.to_decimal(booking.discount_amount, 0)
            if refund_amount < 0:
                raise ServiceException(message='退款金额不能小于0')
            if refund_amount > 0 and booking.pay_status != 1:
                raise ServiceException(message='未付款的预订单不能退款')
            if refund_amount > paid_amount:
                raise ServiceException(message=f'退款金额不能超过实收金额{paid_amount}')
            booking.booking_status = 3
            booking.cancel_reason = page_object.cancel_reason
            booking.refund_amount = refund_amount
            if refund_amount > 0 and booking.pay_status == 1:
                booking.pay_status = 2
            booking.update_by = operator_name
            await TeachVenueDao.edit_booking(query_db, booking)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='取消成功')
        except Exception as e:
            await query_db.rollback()
            raise e
