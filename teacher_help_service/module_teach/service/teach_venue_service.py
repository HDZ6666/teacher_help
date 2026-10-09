import math
import re
from datetime import date, datetime, time
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_venue_dao import TeachVenueDao
from module_teach.entity.do.teach_venue_do import (
    TeachCourt,
    TeachCourtBooking,
    TeachCourtTime,
    TeachVenue,
)
from module_teach.entity.vo.teach_venue_vo import (
    AddTeachBookingModel,
    AddTeachCourtModel,
    AddTeachVenueModel,
    CancelBookingModel,
    ChangeTeachVenueStatusModel,
    DeleteTeachCourtModel,
    DeleteTeachVenueModel,
    EditTeachCourtModel,
    EditTeachVenueModel,
    LockCourtBookingModel,
    TeachBookingGridQueryModel,
    TeachBookingPageQueryModel,
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
    def calc_booking_amount(cls, court: TeachCourt, start_time: str, end_time: str):
        """
        按场地价格由后端计算应收金额（不信任前端传入金额）：
        配置了半小时价格时按半小时向上取整计费；否则按小时价格按分钟折算；均未配置时为 0
        """
        minutes = cls.time_to_minutes(end_time) - cls.time_to_minutes(start_time)
        half_price = cls.to_decimal(court.price_per_half_hour, 0)
        hour_price = cls.to_decimal(court.price_per_hour, 0)
        if half_price > 0:
            amount = half_price * math.ceil(minutes / 30)
        elif hour_price > 0:
            amount = hour_price * Decimal(minutes) / Decimal(60)
        else:
            amount = Decimal('0')
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

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
        rows = []
        for court in courts:
            row = CamelCaseUtil.transform_result(court)
            row['times'] = time_map.get(court.id, [])
            rows.append(row)
        return rows

    @classmethod
    async def get_court_detail_services(cls, query_db: AsyncSession, court_id: int):
        court = await TeachVenueDao.get_court_by_id(query_db, court_id)
        if not court:
            raise ServiceException(message='场地不存在')
        times = await TeachVenueDao.get_times_by_court_id(query_db, court_id)
        row = CamelCaseUtil.transform_result(court)
        row['times'] = [CamelCaseUtil.transform_result(t) for t in times]
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
                        'pricePerHour': court.price_per_hour,
                        'pricePerHalfHour': court.price_per_half_hour,
                    }
                )
            grid.append(
                {
                    'courtId': court.id,
                    'courtName': court.court_name,
                    'courtType': court.court_type,
                    'pricePerHour': court.price_per_hour,
                    'pricePerHalfHour': court.price_per_half_hour,
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
            await cls.assert_no_conflict(query_db, court.id, booking_date, start_time, end_time)
            now = datetime.now()
            booking_type = page_object.booking_type or 'normal'
            amount = cls.calc_booking_amount(court, start_time, end_time)
            discount_amount = cls.to_decimal(page_object.discount_amount, 0)
            if discount_amount < 0 or discount_amount > amount:
                raise ServiceException(message='减免金额不能小于0且不能超过应收金额')
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
    async def lock_court_services(
        cls, query_db: AsyncSession, page_object: LockCourtBookingModel, operator_id, operator_name: str
    ):
        booking_date = cls.parse_date(page_object.booking_date)
        start_time, end_time = cls.validate_time_range(page_object.start_time, page_object.end_time)
        try:
            court = await cls.lock_bookable_court(query_db, page_object.court_id)
            await cls.assert_no_conflict(query_db, court.id, booking_date, start_time, end_time)
            now = datetime.now()
            booking = TeachCourtBooking(
                booking_no=cls.make_booking_no(),
                court_id=court.id,
                court_name=court.court_name,
                venue_id=court.venue_id,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                booking_type='lock',
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
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='锁场成功', result={'id': booking.id})
        except Exception as e:
            await query_db.rollback()
            raise e

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
