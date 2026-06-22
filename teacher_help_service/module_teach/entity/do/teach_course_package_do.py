from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT
from config.database import Base


class TeachCoursePackage(Base):
    """
    课程套餐基础信息表
    """

    __tablename__ = 'teach_course_package'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    package_no = Column(String(50), nullable=True, unique=True, comment='套餐编号')
    package_name = Column(String(100), nullable=False, comment='套餐名称')
    total_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='套餐总价')
    online_sale = Column(SMALLINT, nullable=True, default=0, comment='线上售卖状态(0=未售卖 1=售卖)')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
