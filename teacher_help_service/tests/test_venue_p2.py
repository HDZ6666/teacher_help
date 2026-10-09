"""
场地（P2）：分时价格规则计费、报价、批量锁场（日期范围/星期/多场地）与按批次解除、业务规则开关
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from tests.helpers import raises_service
from config.env import BusinessRuleConfig
from module_teach.entity.do.teach_card_do import TeachCard
from module_teach.entity.do.teach_venue_do import TeachCourt, TeachCourtBooking, TeachCourtPriceRule, TeachVenue
from module_teach.entity.vo.teach_card_vo import AddTeachCardModel
from module_teach.entity.vo.teach_venue_vo import (
    AddTeachBookingModel,
    AddTeachCourtModel,
    CancelLockGroupModel,
    EditTeachCourtModel,
    LockCourtBookingModel,
    TeachBookingQuoteQueryModel,
)
from module_teach.service.teach_card_service import TeachCardService
from module_teach.service.teach_venue_service import TeachVenueService

# 固定使用下周一，保证星期确定
NEXT_MONDAY = date.today() + timedelta(days=7 - date.today().weekday())


def rule(week_day, start, end, hour=0, half=0, rule_id=None):
    return TeachCourtPriceRule(
        id=rule_id, week_day=week_day, start_time=start, end_time=end, price_per_hour=hour, price_per_half_hour=half
    )


def test_no_rules_keeps_p1_amount():
    court = TeachCourt(price_per_hour=Decimal('100'), price_per_half_hour=Decimal('0'))
    assert TeachVenueService.calc_booking_amount(court, '09:00', '10:30', []) == Decimal('150.00')
    court = TeachCourt(price_per_hour=Decimal('100'), price_per_half_hour=Decimal('60'))
    assert TeachVenueService.calc_booking_amount(court, '09:00', '10:10', []) == Decimal('180.00')


def test_rule_overrides_part_of_booking():
    court = TeachCourt(price_per_hour=Decimal('100'), price_per_half_hour=Decimal('0'))
    # 18:00 之后为高峰价 200/小时：17:00-19:00 = 1h*100 + 1h*200
    rules = [rule(1, '18:00', '22:00', hour=Decimal('200'), rule_id=1)]
    assert TeachVenueService.calc_booking_amount(court, '17:00', '19:00', rules) == Decimal('300.00')
    segments = TeachVenueService.split_by_price_rules(court, '17:00', '19:00', rules)
    assert [(s[0], s[1], s[4]) for s in segments] == [(17 * 60, 18 * 60, None), (18 * 60, 19 * 60, 1)]


def test_rule_with_half_hour_price_rounds_up():
    court = TeachCourt(price_per_hour=Decimal('100'), price_per_half_hour=Decimal('0'))
    rules = [rule(1, '18:00', '22:00', half=Decimal('80'), rule_id=1)]
    # 18:00-19:10：70 分钟，按最后一段半小时价向上取整为 3 个半小时
    assert TeachVenueService.calc_booking_amount(court, '18:00', '19:10', rules) == Decimal('240.00')


async def make_venue(db):
    venue = TeachVenue(venue_name='P2场馆', status=1)
    db.add(venue)
    await db.flush()
    await db.commit()
    return venue.id


async def add_court(db, venue_id, name='1号场', price_rules=None):
    result = await TeachVenueService.add_court_services(
        db,
        AddTeachCourtModel(
            venueId=venue_id, courtName=name, pricePerHour=Decimal('100'), priceRules=price_rules or []
        ),
        'op',
    )
    return result.result['id']


async def test_save_price_rules_validation_and_booking(db):
    venue_id = await make_venue(db)
    with raises_service('重叠'):
        await add_court(
            db,
            venue_id,
            price_rules=[
                {'weekDay': 1, 'startTime': '18:00', 'endTime': '20:00', 'pricePerHour': 200},
                {'weekDay': 1, 'startTime': '19:00', 'endTime': '21:00', 'pricePerHour': 200},
            ],
        )
    with raises_service('星期'):
        await add_court(db, venue_id, price_rules=[{'weekDay': 8, 'startTime': '18:00', 'endTime': '20:00'}])
    court_id = await add_court(
        db, venue_id, price_rules=[{'weekDay': NEXT_MONDAY.isoweekday(), 'startTime': '18:00', 'endTime': '22:00',
                                    'pricePerHour': 200}]
    )
    detail = await TeachVenueService.get_court_detail_services(db, court_id)
    assert len(detail['priceRules']) == 1

    quote = await TeachVenueService.get_booking_quote_services(
        db,
        TeachBookingQuoteQueryModel(
            courtId=court_id, bookingDate=NEXT_MONDAY.strftime('%Y-%m-%d'), startTime='17:00', endTime='19:00'
        ),
    )
    assert quote['amount'] == Decimal('300.00') and quote['available'] and len(quote['segments']) == 2

    booking = await TeachVenueService.add_booking_services(
        db,
        AddTeachBookingModel(
            courtId=court_id, bookingDate=NEXT_MONDAY.strftime('%Y-%m-%d'), startTime='17:00', endTime='19:00'
        ),
        1,
        'op',
    )
    assert booking.result['amount'] == Decimal('300.00')
    # 其他星期不受规则影响
    other_day = (NEXT_MONDAY + timedelta(days=1)).strftime('%Y-%m-%d')
    booking = await TeachVenueService.add_booking_services(
        db, AddTeachBookingModel(courtId=court_id, bookingDate=other_day, startTime='17:00', endTime='19:00'), 1, 'op'
    )
    assert booking.result['amount'] == Decimal('200.00')

    # 编辑时不传 priceRules 保持不变，传空数组清空
    await TeachVenueService.edit_court_services(
        db, EditTeachCourtModel(id=court_id, venueId=venue_id, courtName='1号场', pricePerHour=100), 'op'
    )
    assert len((await TeachVenueService.get_court_detail_services(db, court_id))['priceRules']) == 1
    await TeachVenueService.edit_court_services(
        db, EditTeachCourtModel(id=court_id, venueId=venue_id, courtName='1号场', pricePerHour=100, priceRules=[]),
        'op',
    )
    assert (await TeachVenueService.get_court_detail_services(db, court_id))['priceRules'] == []


async def test_add_booking_rejects_lock_type(db):
    venue_id = await make_venue(db)
    court_id = await add_court(db, venue_id)
    with raises_service('锁场功能'):
        await TeachVenueService.add_booking_services(
            db,
            AddTeachBookingModel(
                courtId=court_id, bookingDate=NEXT_MONDAY.strftime('%Y-%m-%d'), startTime='09:00', endTime='10:00',
                bookingType='lock',
            ),
            1,
            'op',
        )


def lock_form(court_id, start_date, end_date=None, week_days=None, court_ids=None, start='09:00', end='10:00'):
    return LockCourtBookingModel(
        courtId=court_id,
        bookingDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d') if end_date else None,
        weekDays=week_days,
        courtIds=court_ids,
        startTime=start,
        endTime=end,
        cancelReason='赛事',
    )


async def test_batch_lock_by_range_weekdays_and_courts(db):
    venue_id = await make_venue(db)
    court_a = await add_court(db, venue_id, '1号场')
    court_b = await add_court(db, venue_id, '2号场')
    # 两周内每周一、周三，两个场地：2 * 2 * 2 = 8 条
    result = await TeachVenueService.lock_court_services(
        db,
        lock_form(
            court_a, NEXT_MONDAY, NEXT_MONDAY + timedelta(days=13), week_days=[1, 3], court_ids=[court_a, court_b]
        ),
        1,
        'op',
    )
    assert result.result['count'] == 8
    group_no = result.result['lockGroupNo']
    assert group_no
    # 锁定时段不能再预订
    with raises_service('已被预订'):
        await TeachVenueService.add_booking_services(
            db,
            AddTeachBookingModel(
                courtId=court_b, bookingDate=NEXT_MONDAY.strftime('%Y-%m-%d'), startTime='09:30', endTime='10:30'
            ),
            1,
            'op',
        )
    # 解除第二周的锁场
    result = await TeachVenueService.cancel_lock_group_services(
        db,
        CancelLockGroupModel(lockGroupNo=group_no, fromDate=(NEXT_MONDAY + timedelta(days=7)).strftime('%Y-%m-%d')),
        'op',
    )
    assert result.result['count'] == 4
    with raises_service('没有可解除'):
        await TeachVenueService.cancel_lock_group_services(
            db,
            CancelLockGroupModel(
                lockGroupNo=group_no, fromDate=(NEXT_MONDAY + timedelta(days=7)).strftime('%Y-%m-%d')
            ),
            'op',
        )


async def test_batch_lock_is_all_or_nothing(db):
    venue_id = await make_venue(db)
    court_id = await add_court(db, venue_id)
    wednesday = NEXT_MONDAY + timedelta(days=2)
    await TeachVenueService.add_booking_services(
        db,
        AddTeachBookingModel(
            courtId=court_id, bookingDate=wednesday.strftime('%Y-%m-%d'), startTime='09:00', endTime='10:00'
        ),
        1,
        'op',
    )
    with raises_service('未锁场'):
        await TeachVenueService.lock_court_services(
            db, lock_form(court_id, NEXT_MONDAY, NEXT_MONDAY + timedelta(days=6)), 1, 'op'
        )
    query = TeachCourtBooking.__table__.select().where(TeachCourtBooking.booking_type == 'lock')
    rows = (await db.execute(query)).all()
    assert rows == []


async def test_batch_lock_limits(db, monkeypatch):
    venue_id = await make_venue(db)
    court_id = await add_court(db, venue_id)
    with raises_service('不能早于'):
        await TeachVenueService.lock_court_services(
            db, lock_form(court_id, NEXT_MONDAY, NEXT_MONDAY - timedelta(days=1)), 1, 'op'
        )
    with raises_service('不能超过一年'):
        await TeachVenueService.lock_court_services(
            db, lock_form(court_id, NEXT_MONDAY, NEXT_MONDAY + timedelta(days=400)), 1, 'op'
        )
    monkeypatch.setattr(BusinessRuleConfig, 'venue_lock_batch_max', 3)
    with raises_service('单次最多锁场3条'):
        await TeachVenueService.lock_court_services(
            db, lock_form(court_id, NEXT_MONDAY, NEXT_MONDAY + timedelta(days=6)), 1, 'op'
        )


async def test_single_lock_keeps_p1_shape(db):
    venue_id = await make_venue(db)
    court_id = await add_court(db, venue_id)
    result = await TeachVenueService.lock_court_services(db, lock_form(court_id, NEXT_MONDAY), 1, 'op')
    assert result.result['count'] == 1 and result.result['lockGroupNo'] is None


async def test_require_open_time_switch(db, monkeypatch):
    venue_id = await make_venue(db)
    result = await TeachVenueService.add_court_services(
        db,
        AddTeachCourtModel(
            venueId=venue_id,
            courtName='限时场',
            pricePerHour=Decimal('100'),
            times=[{'weekDay': NEXT_MONDAY.isoweekday(), 'startTime': '08:00', 'endTime': '12:00'}],
        ),
        'op',
    )
    court_id = result.result['id']
    form = AddTeachBookingModel(
        courtId=court_id, bookingDate=NEXT_MONDAY.strftime('%Y-%m-%d'), startTime='11:00', endTime='13:00'
    )
    monkeypatch.setattr(BusinessRuleConfig, 'venue_booking_require_open_time', True)
    with raises_service('可约时段'):
        await TeachVenueService.add_booking_services(db, form, 1, 'op')
    monkeypatch.setattr(BusinessRuleConfig, 'venue_booking_require_open_time', False)
    assert (await TeachVenueService.add_booking_services(db, form, 1, 'op')).is_success


@pytest.mark.parametrize(
    'mode, rate, expected',
    [
        ('auto', '0.8', Decimal('0.8')),
        ('auto', '8', Decimal('0.8')),
        ('ratio', '0.85', Decimal('0.85')),
        ('zhe', '0.8', Decimal('0.08')),
        ('zhe', '8.5', Decimal('0.85')),
    ],
)
def test_discount_rate_modes(monkeypatch, mode, rate, expected):
    monkeypatch.setattr(BusinessRuleConfig, 'card_discount_rate_mode', mode)
    assert TeachCardService.resolve_pay_ratio(Decimal(rate)) == expected


@pytest.mark.parametrize('mode, rate', [('ratio', '8'), ('zhe', '12'), ('auto', '0'), ('auto', '11')])
def test_discount_rate_modes_invalid(monkeypatch, mode, rate):
    monkeypatch.setattr(BusinessRuleConfig, 'card_discount_rate_mode', mode)
    with raises_service('折扣率'):
        TeachCardService.resolve_pay_ratio(Decimal(rate))


async def test_card_template_validation(db):
    with raises_service('折扣率'):
        await TeachCardService.add_teach_card_services(
            db, AddTeachCardModel(cardName='折扣卡', cardType='venue_discount', discountRate=Decimal('0')), 'op'
        )
    with raises_service('卡类型'):
        await TeachCardService.add_teach_card_services(db, AddTeachCardModel(cardName='x', cardType='bad'), 'op')
    result = await TeachCardService.add_teach_card_services(
        db, AddTeachCardModel(cardName='八折卡', cardType='venue_discount', discountRate=Decimal('0.8')), 'op'
    )
    card = await db.get(TeachCard, result.result['id'])
    assert card.discount_rate == Decimal('0.8')


async def test_grant_list_carries_card_type(db):
    from module_teach.entity.do.teach_card_do import TeachCardGrant
    from module_teach.entity.vo.teach_card_vo import TeachCardGrantPageQueryModel

    card = TeachCard(card_name='场地卡', card_type='venue_discount', discount_rate=Decimal('0.8'))
    db.add(card)
    await db.flush()
    db.add(TeachCardGrant(card_id=card.id, card_name=card.card_name, student_id=1, grant_status=1))
    await db.commit()
    page = await TeachCardService.get_teach_card_grant_list_services(
        db, TeachCardGrantPageQueryModel(pageNum=1, pageSize=10), '', is_page=True
    )
    row = page.rows[0]
    assert row['cardType'] == 'venue_discount' and row['cardTypeName'] == '场地折扣卡'
    assert row['grantStatusName'] == '有效'
    cards = await TeachCardService.get_student_cards_services(db, 1)
    assert cards[0]['cardType'] == 'venue_discount'
