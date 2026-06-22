from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT, ForeignKey
from config.database import Base


class TeachCoursePrice(Base):
    """
    课程定价标准表
    """

    __tablename__ = 'teach_course_price'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    course_id = Column(Integer, ForeignKey('teach_course.id'), nullable=False, comment='课程ID')
    charge_type = Column(String(20), nullable=False, comment='收费方式(class=按课时 month=按月 day=按天)')
    price_name = Column(String(100), nullable=False, default='单价', comment='定价名称')
    quantity = Column(Integer, nullable=False, default=1, comment='购买数量')
    total_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='总价')
    unit_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='单价')
    deduct_rule = Column(String(32), nullable=True, comment='扣课时规则')
    absence_rule = Column(String(32), nullable=True, comment='未到扣课时规则')
    sort = Column(Integer, nullable=True, default=0, comment='排序')
    status = Column(SMALLINT, nullable=True, default=1, comment='状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
