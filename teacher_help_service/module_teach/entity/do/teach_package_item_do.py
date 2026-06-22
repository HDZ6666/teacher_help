from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT, ForeignKey
from config.database import Base


class TeachPackageItem(Base):
    """
    课程套餐明细表
    """

    __tablename__ = 'teach_package_item'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    package_id = Column(Integer, ForeignKey('teach_course_package.id'), nullable=False, comment='套餐ID')
    item_type = Column(String(20), nullable=False, comment='项目类型(course=课程 item=物品 fee=费用)')
    item_id = Column(Integer, nullable=False, comment='项目ID')
    item_name = Column(String(100), nullable=False, comment='项目名称')
    spec_id = Column(Integer, nullable=True, comment='规格或定价ID')
    spec_name = Column(String(100), nullable=True, comment='规格或定价名称')
    unit = Column(String(20), nullable=True, comment='单位')
    quantity = Column(Integer, nullable=False, default=1, comment='购买数量')
    gift_quantity = Column(Integer, nullable=True, default=0, comment='赠送数量')
    leave_free_quantity = Column(Integer, nullable=True, default=0, comment='请假免扣次数')
    unit_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='单价')
    total_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='总价')
    discount_type = Column(String(20), nullable=True, default='reduce', comment='优惠类型(reduce=直减 discount=折扣)')
    discount_value = Column(DECIMAL(10, 2), nullable=True, default=0, comment='优惠值')
    subtotal_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='小计')
    sort = Column(Integer, nullable=True, default=0, comment='排序')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
