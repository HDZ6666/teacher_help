from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT
from config.database import Base


class AstFeeItem(Base):
    """
    费用项目表
    """

    __tablename__ = 'ast_fee_item'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    fee_name = Column(String(100), nullable=False, comment='费用名称')
    amount = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment='费用金额')
    online_sale = Column(SMALLINT, nullable=True, default=0, comment='线上售卖状态(0=关闭 1=开启)')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    sort = Column(Integer, nullable=True, default=0, comment='排序')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
