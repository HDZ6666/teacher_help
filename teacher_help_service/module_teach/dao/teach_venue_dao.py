from datetime import datetime
from sqlalchemy import and_, desc, or_, select, update  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.dept_do import SysDept  # noqa: F401
from module_admin.entity.do.role_do import SysRoleDept  # noqa: F401
from module_teach.entity.do.teach_venue_do import (
    TeachCourt,
    TeachCourtBooking,
    TeachCourtTime,
    TeachVenue,
)
from module_teach.entity.vo.teach_venue_vo import (
    TeachBookingPageQueryModel,
    TeachVenuePageQueryModel,
)
from utils.page_util import PageUtil


class TeachVenueDao:
    """
    场地管理模块数据库操作层
    """

    # ======================== 场馆 ========================
    @classmethod
    async def get_venue_list(
        cls, db: AsyncSession, query_object: TeachVenuePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachVenue).where(TeachVenue.del_flag == 0)
        if query_object.venue_name:
            query = query.where(TeachVenue.venue_name.like(f'%{query_object.venue_name}%'))
        if query_object.status is not None:
            query = query.where(TeachVenue.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachVenue.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachVenue.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachVenue.create_time), desc(TeachVenue.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_venue_by_id(cls, db: AsyncSession, venue_id: int):
        result = await db.execute(select(TeachVenue).where(TeachVenue.id == venue_id, TeachVenue.del_flag == 0))
        return result.scalars().first()

    @classmethod
    async def get_venue_by_no(cls, db: AsyncSession, venue_no: str):
        result = await db.execute(select(TeachVenue).where(TeachVenue.venue_no == venue_no, TeachVenue.del_flag == 0))
        return result.scalars().first()

    @classmethod
    async def add_venue(cls, db: AsyncSession, venue: TeachVenue):
        db.add(venue)
        await db.flush()
        await db.refresh(venue)
        return venue

    @classmethod
    async def edit_venue(cls, db: AsyncSession, venue: TeachVenue):
        venue.update_time = datetime.now()
        await db.flush()
        return venue

    @classmethod
    async def delete_venue(cls, db: AsyncSession, venue_ids: list[int], update_by: str):
        await db.execute(
            update(TeachVenue)
            .where(and_(TeachVenue.id.in_(venue_ids), TeachVenue.del_flag == 0))
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def update_venue_status(cls, db: AsyncSession, venue_id: int, status: int, update_by: str):
        await db.execute(
            update(TeachVenue)
            .where(and_(TeachVenue.id == venue_id, TeachVenue.del_flag == 0))
            .values(status=status, update_by=update_by, update_time=datetime.now())
        )

    # ======================== 场地 ========================
    @classmethod
    async def get_court_list(cls, db: AsyncSession, venue_id: int | None = None, **filters):
        query = select(TeachCourt).where(TeachCourt.del_flag == 0)
        if venue_id is not None:
            query = query.where(TeachCourt.venue_id == venue_id)
        if filters.get('court_name'):
            query = query.where(TeachCourt.court_name.like(f"%{filters['court_name']}%"))
        if filters.get('court_type'):
            query = query.where(TeachCourt.court_type == filters['court_type'])
        if filters.get('status') is not None:
            query = query.where(TeachCourt.status == filters['status'])
        query = query.order_by(desc(TeachCourt.create_time), desc(TeachCourt.id))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_courts_by_venue_id(cls, db: AsyncSession, venue_id: int):
        result = await db.execute(
            select(TeachCourt)
            .where(TeachCourt.venue_id == venue_id, TeachCourt.del_flag == 0)
            .order_by(TeachCourt.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_court_by_id(cls, db: AsyncSession, court_id: int, for_update: bool = False):
        query = select(TeachCourt).where(TeachCourt.id == court_id, TeachCourt.del_flag == 0)
        if for_update:
            # 锁定场地行，串行化同一场地的预订/锁场，避免并发撞场
            await db.flush()
            query = query.with_for_update().execution_options(populate_existing=True)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def add_court(cls, db: AsyncSession, court: TeachCourt):
        db.add(court)
        await db.flush()
        await db.refresh(court)
        return court

    @classmethod
    async def edit_court(cls, db: AsyncSession, court: TeachCourt):
        court.update_time = datetime.now()
        await db.flush()
        return court

    @classmethod
    async def delete_court(cls, db: AsyncSession, court_ids: list[int], update_by: str):
        await db.execute(
            update(TeachCourt)
            .where(and_(TeachCourt.id.in_(court_ids), TeachCourt.del_flag == 0))
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    # ======================== 可约时段 ========================
    @classmethod
    async def get_times_by_court_id(cls, db: AsyncSession, court_id: int):
        result = await db.execute(
            select(TeachCourtTime)
            .where(TeachCourtTime.court_id == court_id)
            .order_by(TeachCourtTime.week_day, TeachCourtTime.start_time, TeachCourtTime.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_times_by_court_ids(cls, db: AsyncSession, court_ids: list[int]):
        if not court_ids:
            return []
        result = await db.execute(
            select(TeachCourtTime)
            .where(TeachCourtTime.court_id.in_(court_ids))
            .order_by(TeachCourtTime.court_id, TeachCourtTime.week_day, TeachCourtTime.start_time, TeachCourtTime.id)
        )
        return result.scalars().all()

    @classmethod
    async def add_court_time(cls, db: AsyncSession, court_time: TeachCourtTime):
        db.add(court_time)
        await db.flush()
        return court_time

    @classmethod
    async def delete_times_by_court_id(cls, db: AsyncSession, court_id: int):
        from sqlalchemy import delete

        await db.execute(delete(TeachCourtTime).where(TeachCourtTime.court_id == court_id))

    # ======================== 预订单 ========================
    @classmethod
    async def get_booking_list(
        cls, db: AsyncSession, query_object: TeachBookingPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachCourtBooking).where(TeachCourtBooking.del_flag == 0)
        if query_object.venue_id is not None:
            query = query.where(TeachCourtBooking.venue_id == query_object.venue_id)
        if query_object.court_id is not None:
            query = query.where(TeachCourtBooking.court_id == query_object.court_id)
        if query_object.booking_no:
            query = query.where(TeachCourtBooking.booking_no.like(f'%{query_object.booking_no}%'))
        if query_object.customer_name:
            query = query.where(TeachCourtBooking.customer_name.like(f'%{query_object.customer_name}%'))
        if query_object.customer_phone:
            query = query.where(TeachCourtBooking.customer_phone.like(f'%{query_object.customer_phone}%'))
        if query_object.booking_type:
            query = query.where(TeachCourtBooking.booking_type == query_object.booking_type)
        if query_object.booking_status is not None:
            query = query.where(TeachCourtBooking.booking_status == query_object.booking_status)
        if query_object.pay_status is not None:
            query = query.where(TeachCourtBooking.pay_status == query_object.pay_status)
        if query_object.booking_date:
            query = query.where(TeachCourtBooking.booking_date == query_object.booking_date)
        if query_object.begin_time:
            query = query.where(TeachCourtBooking.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachCourtBooking.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachCourtBooking.booking_date), desc(TeachCourtBooking.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_booking_by_id(cls, db: AsyncSession, booking_id: int, for_update: bool = False):
        query = select(TeachCourtBooking).where(TeachCourtBooking.id == booking_id, TeachCourtBooking.del_flag == 0)
        if for_update:
            # 核销/取消前加锁读取，防止并发重复核销或核销与取消交叉
            await db.flush()
            query = query.with_for_update().execution_options(populate_existing=True)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_bookings_by_date(cls, db: AsyncSession, court_ids: list[int], booking_date):
        """获取指定场地集合在某日的有效预订(已预订/已核销)"""
        if not court_ids:
            return []
        result = await db.execute(
            select(TeachCourtBooking).where(
                TeachCourtBooking.court_id.in_(court_ids),
                TeachCourtBooking.booking_date == booking_date,
                TeachCourtBooking.del_flag == 0,
                TeachCourtBooking.booking_status.in_([1, 2]),
            )
        )
        return result.scalars().all()

    @classmethod
    async def get_conflict_bookings(cls, db: AsyncSession, court_id: int, booking_date, start_time: str, end_time: str):
        """
        同场地同日时间段冲突查询：返回与[start_time, end_time)重叠的有效预订单。
        重叠判定：existing.start_time < end_time AND existing.end_time > start_time
        时间均为补零后的 HH:MM 字符串（Service 层 normalize_time 保证，存量数据由 V002 迁移补零），字典序即时间先后
        有效状态：booking_status in (1已预订, 2已核销)
        """
        result = await db.execute(
            select(TeachCourtBooking).where(
                TeachCourtBooking.court_id == court_id,
                TeachCourtBooking.booking_date == booking_date,
                TeachCourtBooking.del_flag == 0,
                TeachCourtBooking.booking_status.in_([1, 2]),
                TeachCourtBooking.start_time < end_time,
                TeachCourtBooking.end_time > start_time,
            )
        )
        return result.scalars().all()

    @classmethod
    async def add_booking(cls, db: AsyncSession, booking: TeachCourtBooking):
        db.add(booking)
        await db.flush()
        await db.refresh(booking)
        return booking

    @classmethod
    async def edit_booking(cls, db: AsyncSession, booking: TeachCourtBooking):
        booking.update_time = datetime.now()
        await db.flush()
        return booking
