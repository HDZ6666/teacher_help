from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL, SMALLINT
from config.database import Base


class TeachCard(Base):
    """
    会员卡模板表
    """

    __tablename__ = 'teach_card'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    card_no = Column(String(50), nullable=True, unique=True, comment='卡编号')
    card_name = Column(String(100), nullable=False, comment='卡名称')
    card_type = Column(String(20), nullable=False, default='course', comment='卡类型(course=课程卡 venue_discount=场地折扣卡)')
    initial_count = Column(Integer, nullable=True, default=0, comment='初始次数(课程卡)')
    valid_days = Column(Integer, nullable=True, default=0, comment='有效天数')
    effect_type = Column(String(20), nullable=True, default='immediate', comment='生效方式(immediate=立即 first_use=首次使用后)')
    discount_rate = Column(DECIMAL(5, 2), nullable=True, default=0, comment='折扣率(场地折扣卡)')
    cover_image = Column(String(500), nullable=True, comment='封面图')
    price = Column(DECIMAL(10, 2), nullable=True, default=0, comment='售价')
    online_sale = Column(SMALLINT, nullable=True, default=0, comment='线上售卖状态(0=未售卖 1=售卖)')
    description = Column(String(500), nullable=True, comment='卡说明')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachCardCourse(Base):
    """
    会员卡适用课程表
    """

    __tablename__ = 'teach_card_course'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    card_id = Column(Integer, nullable=False, comment='卡ID')
    course_id = Column(Integer, nullable=False, comment='课程ID')
    course_name = Column(String(100), nullable=True, comment='课程名称快照')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')


class TeachCardGrant(Base):
    """
    会员卡发放记录表
    """

    __tablename__ = 'teach_card_grant'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    grant_no = Column(String(50), nullable=True, unique=True, comment='发放编号')
    card_id = Column(Integer, nullable=False, comment='卡ID')
    card_name = Column(String(100), nullable=True, comment='卡名称快照')
    student_id = Column(Integer, nullable=False, comment='学员ID')
    student_name = Column(String(50), nullable=True, comment='学员姓名快照')
    grant_count = Column(Integer, nullable=True, default=0, comment='发放次数')
    remaining_count = Column(Integer, nullable=True, default=0, comment='剩余次数')
    valid_start_date = Column(Date, nullable=True, comment='生效日期')
    valid_end_date = Column(Date, nullable=True, comment='失效日期')
    grant_status = Column(SMALLINT, nullable=True, default=1, comment='发放状态(1=有效 2=过期 3=用完 4=作废)')
    operator_id = Column(Integer, nullable=True, comment='操作人ID')
    operator_name = Column(String(50), nullable=True, comment='操作人姓名')
    grant_time = Column(DateTime, nullable=True, default=datetime.now, comment='发放时间')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachCardLog(Base):
    """
    会员卡操作记录表
    """

    __tablename__ = 'teach_card_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    card_id = Column(Integer, nullable=True, comment='卡ID')
    grant_id = Column(Integer, nullable=True, comment='发放记录ID')
    student_id = Column(Integer, nullable=True, comment='学员ID')
    action = Column(String(20), nullable=False, comment='操作类型(grant=发放 consume=消耗 void=作废 expire=过期)')
    change_count = Column(Integer, nullable=True, default=0, comment='变动次数')
    before_count = Column(Integer, nullable=True, default=0, comment='变动前次数')
    after_count = Column(Integer, nullable=True, default=0, comment='变动后次数')
    operator_id = Column(Integer, nullable=True, comment='操作人ID')
    operator_name = Column(String(50), nullable=True, comment='操作人姓名')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    remark = Column(String(500), nullable=True, comment='备注')
