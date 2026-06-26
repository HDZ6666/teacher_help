from datetime import datetime
from sqlalchemy import Column, Date, DateTime, DECIMAL, ForeignKey, Integer, SMALLINT, String
from config.database import Base


class TeachVenue(Base):
    """
    场馆信息表
    """

    __tablename__ = 'teach_venue'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    venue_no = Column(String(50), nullable=True, unique=True, comment='场馆编号')
    venue_name = Column(String(100), nullable=False, comment='场馆名称')
    address = Column(String(255), nullable=True, comment='场馆地址')
    description = Column(String(500), nullable=True, comment='场馆描述')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachCourt(Base):
    """
    场地信息表
    """

    __tablename__ = 'teach_court'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    venue_id = Column(Integer, ForeignKey('teach_venue.id'), nullable=False, comment='所属场馆ID')
    venue_name = Column(String(100), nullable=True, comment='场馆名称快照')
    court_no = Column(String(50), nullable=True, comment='场地编号')
    court_name = Column(String(100), nullable=False, comment='场地名称')
    court_type = Column(String(50), nullable=True, comment='场地类型(如篮球/羽毛球)')
    price_per_hour = Column(DECIMAL(10, 2), nullable=True, default=0, comment='每小时价格')
    price_per_half_hour = Column(DECIMAL(10, 2), nullable=True, default=0, comment='每半小时价格')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachCourtTime(Base):
    """
    场地可约时段表
    """

    __tablename__ = 'teach_court_time'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    court_id = Column(Integer, ForeignKey('teach_court.id'), nullable=False, comment='场地ID')
    week_day = Column(SMALLINT, nullable=False, comment='星期(1-7)')
    start_time = Column(String(10), nullable=False, comment='开始时间')
    end_time = Column(String(10), nullable=False, comment='结束时间')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')


class TeachCourtBooking(Base):
    """
    场地预订单表
    """

    __tablename__ = 'teach_court_booking'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    booking_no = Column(String(50), nullable=True, unique=True, comment='预订单编号')
    court_id = Column(Integer, ForeignKey('teach_court.id'), nullable=False, comment='场地ID')
    court_name = Column(String(100), nullable=True, comment='场地名称快照')
    venue_id = Column(Integer, nullable=True, comment='所属场馆ID')
    booking_date = Column(Date, nullable=False, comment='预订日期')
    start_time = Column(String(10), nullable=False, comment='开始时间')
    end_time = Column(String(10), nullable=False, comment='结束时间')
    customer_id = Column(Integer, nullable=True, comment='学员或客户ID')
    customer_name = Column(String(50), nullable=True, comment='客户姓名')
    customer_phone = Column(String(20), nullable=True, comment='客户电话')
    booking_type = Column(String(20), nullable=True, default='normal', comment='预订类型(normal=预订 lock=锁场)')
    origin = Column(String(20), nullable=True, default='admin', comment='来源(admin=代预订 online=线上)')
    amount = Column(DECIMAL(10, 2), nullable=True, default=0, comment='应收金额')
    discount_amount = Column(DECIMAL(10, 2), nullable=True, default=0, comment='优惠金额')
    card_grant_id = Column(Integer, nullable=True, comment='会员卡发放ID(会员卡折扣)')
    pay_status = Column(SMALLINT, nullable=True, default=0, comment='支付状态(0=未付 1=已付 2=已退)')
    booking_status = Column(SMALLINT, nullable=True, default=1, comment='预订状态(1=已预订 2=已核销 3=已取消)')
    verify_time = Column(DateTime, nullable=True, comment='核销时间')
    cancel_reason = Column(String(255), nullable=True, comment='取消原因')
    refund_amount = Column(DECIMAL(10, 2), nullable=True, default=0, comment='退款金额')
    operator_id = Column(Integer, nullable=True, comment='操作人ID')
    operator_name = Column(String(50), nullable=True, comment='操作人姓名')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
