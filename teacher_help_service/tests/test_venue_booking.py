"""
场地预订（P1）：时间规范化与比较、冲突校验、金额后端计算、取消规则
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from tests.helpers import raises_service
from module_teach.entity.do.teach_venue_do import TeachCourt, TeachCourtBooking, TeachVenue
from module_teach.entity.vo.teach_venue_vo import AddTeachBookingModel, CancelBookingModel, VerifyBookingModel
from module_teach.service.teach_venue_service import TeachVenueService

BOOKING_DATE = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')


@pytest.mark.parametrize(
    'raw, expected',
    [('9:00', '09:00'), ('09:00', '09:00'), ('9:30:00', '09:30'), ('23:59', '23:59'), ('24:00', '24:00')],
)
def test_normalize_time(raw, expected):
    assert TeachVenueService.normalize_time(raw) == expected


@pytest.mark.parametrize('raw', ['25:00', '9:60', '24:30', 'abc', '', None])
def test_normalize_time_invalid(raw):
    with raises_service():
        TeachVenueService.normalize_time(raw)


def test_time_range_compares_as_time_not_string():
    # 旧实现按字符串比较，'9:00' >= '10:00' 为真会被误判为非法区间
    assert TeachVenueService.validate_time_range('9:00', '10:00') == ('09:00', '10:00')
    with raises_service():
        TeachVenueService.validate_time_range('10:00', '9:00')


def test_calc_amount():
    court = TeachCourt(price_per_hour=Decimal('100'), price_per_half_hour=Decimal('0'))
    assert TeachVenueService.calc_booking_amount(court, '09:00', '10:30') == Decimal('150.00')
    court = TeachCourt(price_per_hour=Decimal('100'), price_per_half_hour=Decimal('60'))
    # 有半小时价时按半小时向上取整：70 分钟 = 3 个半小时
    assert TeachVenueService.calc_booking_amount(court, '09:00', '10:10') == Decimal('180.00')


async def make_court(db, status=1, venue_status=1):
    venue = TeachVenue(venue_name='测试场馆', status=venue_status)
    db.add(venue)
    await db.flush()
    court = TeachCourt(
        venue_id=venue.id,
        court_name='1号场',
        price_per_hour=Decimal('100'),
        price_per_half_hour=Decimal('0'),
        status=status,
    )
    db.add(court)
    await db.flush()
    await db.commit()
    return court.id


def booking(court_id, start, end, **kwargs):
    return AddTeachBookingModel(courtId=court_id, bookingDate=BOOKING_DATE, startTime=start, endTime=end, **kwargs)


async def test_overlapping_booking_rejected_and_adjacent_allowed(db):
    court_id = await make_court(db)
    first = await TeachVenueService.add_booking_services(db, booking(court_id, '9:00', '10:00', amount=1), 1, 'op')
    # 前端传入的金额不生效，按场地价格计算
    assert first.result['amount'] == Decimal('100.00')
    with raises_service('已被预订'):
        await TeachVenueService.add_booking_services(db, booking(court_id, '09:30', '10:30'), 1, 'op')
    # 不补零的时间同样能识别冲突
    with raises_service('已被预订'):
        await TeachVenueService.add_booking_services(db, booking(court_id, '8:30', '9:30'), 1, 'op')
    # 首尾相接不算冲突
    result = await TeachVenueService.add_booking_services(db, booking(court_id, '10:00', '11:00'), 1, 'op')
    assert result.is_success


async def test_disabled_court_cannot_be_booked(db):
    court_id = await make_court(db, status=0)
    with raises_service('停用'):
        await TeachVenueService.add_booking_services(db, booking(court_id, '9:00', '10:00'), 1, 'op')


async def test_discount_cannot_exceed_amount(db):
    court_id = await make_court(db)
    with raises_service('减免金额'):
        await TeachVenueService.add_booking_services(
            db, booking(court_id, '9:00', '10:00', discountAmount=Decimal('101')), 1, 'op'
        )


async def test_cancel_rules(db):
    court_id = await make_court(db)
    paid = await TeachVenueService.add_booking_services(db, booking(court_id, '9:00', '10:00', payStatus=1), 1, 'op')
    with raises_service('退款金额不能超过'):
        await TeachVenueService.cancel_booking_services(
            db, CancelBookingModel(id=paid.result['id'], refundAmount=Decimal('100.01')), 'op'
        )
    result = await TeachVenueService.cancel_booking_services(
        db, CancelBookingModel(id=paid.result['id'], refundAmount=Decimal('100')), 'op'
    )
    assert result.is_success
    cancelled = await db.get(TeachCourtBooking, paid.result['id'], populate_existing=True)
    assert (cancelled.booking_status, cancelled.pay_status) == (3, 2)

    verified = await TeachVenueService.add_booking_services(db, booking(court_id, '9:00', '10:00'), 1, 'op')
    await TeachVenueService.verify_booking_services(db, VerifyBookingModel(id=verified.result['id']), 'op')
    with raises_service('已核销'):
        await TeachVenueService.cancel_booking_services(db, CancelBookingModel(id=verified.result['id']), 'op')
