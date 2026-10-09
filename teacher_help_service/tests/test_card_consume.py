"""
会员卡核销（P1）：条件扣减、用完置状态、归属/类型/有效期校验、场地折扣卡订场
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from tests.helpers import raises_service
from module_teach.dao.teach_card_dao import TeachCardDao
from module_teach.entity.do.teach_card_do import TeachCard, TeachCardGrant
from module_teach.entity.do.teach_venue_do import TeachCourt, TeachCourtBooking, TeachVenue
from module_teach.entity.vo.teach_card_vo import ConsumeTeachCardGrantModel
from module_teach.entity.vo.teach_venue_vo import AddTeachBookingModel
from module_teach.service.teach_card_service import TeachCardService
from module_teach.service.teach_venue_service import TeachVenueService


async def make_grant(db, card_type='course', remaining=3, student_id=1, valid_days=30, start=None, rate=0):
    card = TeachCard(
        card_name='测试卡', card_type=card_type, initial_count=remaining, valid_days=valid_days, discount_rate=rate
    )
    db.add(card)
    await db.flush()
    start = start if start is not None else date.today()
    grant = TeachCardGrant(
        card_id=card.id,
        card_name=card.card_name,
        student_id=student_id,
        grant_count=remaining,
        remaining_count=remaining,
        valid_start_date=start,
        valid_end_date=start + timedelta(days=valid_days) if start and valid_days else None,
        grant_status=1,
    )
    db.add(grant)
    await db.flush()
    await db.commit()
    return grant.id


def consume(grant_id, count=1, student_id=None):
    return ConsumeTeachCardGrantModel(grantId=grant_id, consumeCount=count, studentId=student_id)


async def test_consume_until_used_up(db):
    grant_id = await make_grant(db, remaining=2)
    result = await TeachCardService.consume_teach_card_grant_services(db, consume(grant_id), 1, 'op')
    assert result.result['remainingCount'] == 1
    result = await TeachCardService.consume_teach_card_grant_services(db, consume(grant_id), 1, 'op')
    assert result.result['remainingCount'] == 0
    grant = await db.get(TeachCardGrant, grant_id, populate_existing=True)
    assert grant.grant_status == TeachCardService.GRANT_STATUS_USED_UP
    with raises_service('用完'):
        await TeachCardService.consume_teach_card_grant_services(db, consume(grant_id), 1, 'op')


async def test_consume_more_than_remaining_rejected(db):
    grant_id = await make_grant(db, remaining=1)
    with raises_service('剩余次数不足'):
        await TeachCardService.consume_teach_card_grant_services(db, consume(grant_id, 2), 1, 'op')
    grant = await db.get(TeachCardGrant, grant_id, populate_existing=True)
    assert grant.remaining_count == 1


async def test_conditional_deduct_guards_concurrent_overdraw(db):
    grant_id = await make_grant(db, remaining=1)
    # 模拟两个事务都读到剩余 1 次：第一次条件扣减成功，第二次因 remaining_count >= 1 不再成立而失败
    assert await TeachCardDao.deduct_grant_count(db, grant_id, 1, TeachCardService.GRANT_STATUS_USED_UP, 'op') == 1
    assert await TeachCardDao.deduct_grant_count(db, grant_id, 1, TeachCardService.GRANT_STATUS_USED_UP, 'op') == 0
    await db.commit()
    grant = await db.get(TeachCardGrant, grant_id, populate_existing=True)
    assert (grant.remaining_count, grant.grant_status) == (0, TeachCardService.GRANT_STATUS_USED_UP)


async def test_owner_and_expiry_checked(db):
    grant_id = await make_grant(db, student_id=7)
    with raises_service('不属于'):
        await TeachCardService.consume_teach_card_grant_services(db, consume(grant_id, student_id=8), 1, 'op')
    expired_id = await make_grant(db, start=date.today() - timedelta(days=40), valid_days=30)
    with raises_service('过期'):
        await TeachCardService.consume_teach_card_grant_services(db, consume(expired_id), 1, 'op')


async def test_first_use_card_starts_validity_on_consume(db):
    grant_id = await make_grant(db, start=None, valid_days=10)
    grant = await db.get(TeachCardGrant, grant_id)
    grant.valid_start_date = None
    grant.valid_end_date = None
    await db.commit()
    await TeachCardService.consume_teach_card_grant_services(db, consume(grant_id), 1, 'op')
    grant = await db.get(TeachCardGrant, grant_id, populate_existing=True)
    assert grant.valid_start_date == date.today()
    assert grant.valid_end_date == date.today() + timedelta(days=10)


@pytest.mark.parametrize('rate, ratio', [(Decimal('0.8'), Decimal('0.8')), (Decimal('8.5'), Decimal('0.85'))])
def test_pay_ratio(rate, ratio):
    assert TeachCardService.resolve_pay_ratio(rate) == ratio


async def test_venue_discount_card_applied_to_booking(db):
    venue = TeachVenue(venue_name='场馆', status=1)
    db.add(venue)
    await db.flush()
    court = TeachCourt(venue_id=venue.id, court_name='A', price_per_hour=Decimal('100'), status=1)
    db.add(court)
    await db.flush()
    await db.commit()
    grant_id = await make_grant(db, card_type='venue_discount', remaining=0, student_id=5, rate=Decimal('8'))
    model = AddTeachBookingModel(
        courtId=court.id,
        bookingDate=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        startTime='9:00',
        endTime='10:00',
        customerId=5,
        cardGrantId=grant_id,
    )
    result = await TeachVenueService.add_booking_services(db, model, 1, 'op')
    booking = await db.get(TeachCourtBooking, result.result['id'])
    assert booking.amount == Decimal('100.00')
    assert booking.discount_amount == Decimal('20.00')
    # 课程卡不能用于订场
    course_grant = await make_grant(db, card_type='course', student_id=5)
    model.card_grant_id = course_grant
    model.start_time, model.end_time = '11:00', '12:00'
    with raises_service('场地折扣卡'):
        await TeachVenueService.add_booking_services(db, model, 1, 'op')
