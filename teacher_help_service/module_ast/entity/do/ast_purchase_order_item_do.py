from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT, ForeignKey
from config.database import Base


class AstPurchaseOrderItem(Base):
    """
    采购单明细表
    """

    __tablename__ = 'ast_purchase_order_item'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    order_id = Column(Integer, ForeignKey('ast_purchase_order.id'), nullable=False, comment='采购单ID')
    item_id = Column(Integer, ForeignKey('ast_item.id'), nullable=False, comment='物品ID')
    item_name = Column(String(100), nullable=False, comment='物品名称')
    sku_id = Column(Integer, ForeignKey('ast_item_sku.id'), nullable=False, comment='SKU ID')
    sku_name = Column(String(100), nullable=False, comment='SKU名称')
    unit_price = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment='采购单价')
    quantity = Column(Integer, nullable=False, default=0, comment='采购数量')
    total_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment='小计金额')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    remark = Column(String(500), nullable=True, comment='备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
