from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Date, SMALLINT, ForeignKey
from config.database import Base


class AstItemStockRecord(Base):
    """
    物品出入库记录表
    """

    __tablename__ = 'ast_item_stock_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    record_no = Column(String(50), nullable=False, unique=True, comment='流水号')
    item_id = Column(Integer, ForeignKey('ast_item.id'), nullable=False, comment='物品ID')
    item_name = Column(String(100), nullable=False, comment='物品名称')
    sku_id = Column(Integer, ForeignKey('ast_item_sku.id'), nullable=False, comment='SKU ID')
    sku_name = Column(String(100), nullable=False, comment='SKU名称')
    business_type = Column(String(20), nullable=False, comment='业务类型')
    quantity = Column(Integer, nullable=False, comment='数量')
    stock_before = Column(Integer, nullable=True, default=0, comment='操作前库存')
    stock_after = Column(Integer, nullable=True, default=0, comment='操作后库存')
    source_type = Column(String(20), nullable=True, comment='来源类型')
    source_id = Column(Integer, nullable=True, comment='来源单据ID')
    related_id = Column(Integer, nullable=True, comment='关联ID')
    related_name = Column(String(50), nullable=True, comment='关联名称')
    related_type = Column(String(20), nullable=True, comment='关联类型')
    operator_id = Column(Integer, nullable=True, comment='操作人ID')
    operator_name = Column(String(50), nullable=True, comment='操作人姓名')
    record_date = Column(Date, nullable=False, comment='记录日期')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    remark = Column(String(500), nullable=True, comment='备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
